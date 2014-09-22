#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import errno
import shutil
import re
import uuid
import subprocess
import json

from settings import *
from omero_import import *
import Ice

def search_files(path, pattern=None, ignore_pattern=None):
    for root, dirs, files in os.walk(path):
        ignored_dirs = filter(lambda d: ignore_pattern.match(os.path.join(root, d)), dirs)
        for d in ignored_dirs:
            dirs.remove(d)
        filtered = files if pattern is None else filter(lambda f: pattern.match(f) is not None, files)
        filtered_out = filtered if ignore_pattern is None else filter(
                lambda f: ignore_pattern.match(os.path.join(root, f)) is None, filtered)
        for f in filtered_out:
            yield (root, f)

def get_owner(path):
    uid = os.stat(path).st_uid
    for uname in USERS:
        for keyword in USERS[uname]['KEYWORDS']:
            if keyword in path:
                return uname

    for uname in USERS:
        if uid in USERS[uname]['UIDS']:
            return uname

    return None

'''
argument: a file path
return: a tuple (a Popen instance, success flag)
can raise OSError, hikaridecon.DeconvoluteError
'''
def deconvolute(**kwargs):
    path = kwargs['path']
    deconvoluted = path + '_decon'
    if not os.path.exists(deconvoluted):
        decon = hikaridecon.run(path)
        decon.wait()
        if decon.returncode != 0:
            fail(hikaridecon.DeconvoluteError, decon.returncode,
                    decon.stderr, path)
    kwargs['path'] = deconvoluted
    return kwargs

def get_error_dict(error):
    retval = {}
    retval['TYPE'] = str(type(error).mro()[0])
    retval['MESSAGE'] = error.message
    retval['STR'] = error.__str__()
    if hasattr(error, 'errno'):
        retval['ERRNO'] = error.errno
    else:
        retval['ERRNO'] = -1
    #if hasattr(error, 'ice_name'):
    #    retval['ICE_NAME'] = error.ice_name
    return retval

def update_error(obj, error, prcname):
    obj['SUCCESS'] = False
    obj['ERROR'] = get_error_dict(error)
    obj['ERROR']['PROCESS'] = prcname

getPassword = lambda uname: USERS[uname]['PASSWORD'] if uname in USERS else None

def connect(**kwargs):
    if 'conn' not in kwargs or kwargs['conn'] is None:
        kwargs['conn'] = tools.connect_to_omero(kwargs['uname'], kwargs['passwd'])
    error = None
    for i in xrange(3): # try to connect 3 times
        try:
            kwargs['dataset'] = tools.get_dataset(kwargs['conn'], os.path.dirname(kwargs['path']))
        except Exception, err:
            close_session(**kwargs)
            kwargs['conn'] = tools.connect_to_omero(kwargs['uname'], kwargs['passwd'])
            error = err
            continue
        error = None
        break
    else:
        if error is not None:
            raise error
    return kwargs

def init_chromatic_shift(**kwargs):
    kwargs['zs'] = ChromaticShift(kwargs['path'])
    return kwargs

def check_not_imported_yet(**kwargs):
    imported = False
    if kwargs['dataset'] is None:
        kwargs['dataset'] = tools.create_dataset(kwargs['conn'], os.path.dirname(kwargs['path']))
    else:
        for image in kwargs['dataset'].listChildren():
            if image.getName() == kwargs['zs'].filename:
                imported = True
                break
    if imported:
        fail(EnvironmentError, errno.EEXIST, 'Have already imported', kwargs['path'])
    return kwargs

'''
argument: a file path
return: the log file path
can raise ValueError, IOError
'''
def get_log(**kwargs):
    path = kwargs['path']
    dirname = os.path.dirname(path)
    name, exp = os.path.basename(path).rsplit('.',1)

    if exp == 'dv':
        name = name.replace('_D3D','')
    logfile = ''.join([dirname, '/', name, '.dv.log'])

    if not os.path.exists(logfile):
        fail(IOError, errno.ENOENT, 'No such file or directory' % logfile, logfile)

    kwargs['logfile'] = logfile
    #kwargs['dest'] = ''.join(['/omeroimports', dirname, '/', kwargs['zs'].filename])
    kwargs['dest'] = os.path.join(dirname, kwargs['zs'].filename)
    kwargs['image_uuid'] = str(uuid.uuid4())

    return kwargs

def run_chromatic_shift(**kwargs):
    if not kwargs['zs'].is_already_done(kwargs['dest']):
        kwargs['zs'].do()
        kwargs['zs'].move(kwargs['dest'])
    return kwargs

def add_log(**kwargs):
    kwargs['retval']['PROCESSES'].append('LOG WRITING')
    if not write_log(kwargs['logfile'], kwargs['dest'], kwargs['image_uuid']):
        fail(IOError, errno.EIO, '%s can not be written to %s.' % (kwargs['logfile'], kwargs['dest']))
    return kwargs

def import_main(**kwargs):
    args = ['/home/pcarlton/OMERO5/OMERO.clients-5.0.3-ice35-b41.linux/importer-cli',
            '-s', 'localhost',
            '-u', kwargs['uname'],
            '-w', kwargs['passwd'],
            '-d', str(kwargs['dataset'].getId()),
            '-n', kwargs['zs'].filename,
            '--','--transfer=ln_s',
            kwargs['dest']]
    import_prc = subprocess.Popen(args, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=False)
    import_prc.wait()
    if import_prc.returncode != 0:
        err_message = '\n'.join(import_prc.stderr.readlines())
        fail(EnvironmentError, import_prc.returncode, err_message, kwargs['path'])
    return kwargs

def succeed(**kwargs):
    default = {'SUCCESS' : True}
    if 'retval' in kwargs:
        kwargs['retval'].update(default)
    else:
        kwargs['retval'] = default
    return kwargs

def unit_process(prcname, func, **kwargs):
    kwargs['retval']['PROCESSES'].append(prcname)
    try:
        kwargs = func(**kwargs)
    except Exception, err:
        update_error(kwargs['retval'], err, prcname)
        raise
    return kwargs

partial_process = lambda prcname, fun: partial(unit_process, prcname, fun)

def close_session(**kwargs):
    if 'conn' in kwargs and kwargs['conn'] is not None:
        kwargs['conn'].seppuku()

'''
!!! path = .*_R3D.dv !!!
'''
def import_file(path, uname=None, passwd=None, conn=None):
    if uname is None or passwd is None:
        uname = get_owner(path)
        passwd = getPassword(uname)
        if passwd is None:
            return ({}, False)

    kwargs = {
            'retval': {'PROCESSES': []},
            'path': path,
            'uname': uname,
            'passwd': passwd,
            'conn': conn}

    if os.path.isdir(path) or not os.path.exists(path):
        return ({}, False)

    if ' ' in path:
        return ({}, False)

    try:
        kwargs = reduce(lambda obj, fun: fun(**obj), [
            partial_process('DECONVOUTION', deconvolute),
            partial_process('CONNECTING', connect),
            partial_process('CHROMATIC SHIFT INIT', init_chromatic_shift),
            partial_process('CHECKING NOT IMIPORTED YET', check_not_imported_yet),
            partial_process('LOG GETTING', get_log),
            partial_process('CHROMATIC SHIFT RUNNING', run_chromatic_shift),
            partial_process('LOG WRITING', add_log),
            partial_process('IMPORTING', import_main),
            succeed
            ], kwargs)
    except Exception, err:
        print >> sys.stderr, err

    if conn is not None:
        close_session(**kwargs)
    return (kwargs['retval'], True)

def import_to_omero(path, pattern=None, ignores=None):
    ignore_pattern = re.compile('|'.join(construct(ignores, r'.*/\..*')))

    result = {}
    connects = {}
    print >> sys.stderr, '[LOG] path: %s' % path
    for dpath, fname in search_files(path, pattern, ignore_pattern):
        fullpath = os.path.join(dpath, fname)
        print >> sys.stderr, '[LOG] checking for "%s"' % fullpath
        if not os.access(fullpath, os.R_OK):
            continue
        owner = get_owner(fullpath)
        if owner not in connects:
            passwd = getPassword(owner)
            if passwd is None:
                continue
            connects[owner] = tools.connect_to_omero(owner, passwd)
        obj, is_completed = import_file(fullpath, owner, passwd, connects[owner])
        if not is_completed:
            continue
        #result[fullpath] = obj
        if 'ERROR' not in obj or 'ERRNO' not in obj['ERROR'] or obj['ERROR']['ERRNO'] != errno.EEXIST:
            print '"%s": %s' % (fullpath, json.dumps(obj))
    for uname, conn in connects:
        close_session(conn=conn)
    return result

def main():
    argv = sys.argv
    argc = len(argv)

    if argc == 1:
        paths = DEFAULT['DIRECTORIES']
    else:
        argv.pop(0)
        paths = argv

    ignores = DEFAULT['IGNORES']
    pattern = re.compile('^(.*)R3D\.dv$')
    # only import files deconvoluted with hikaridecon
    # pattern = re.compile('(.*)(R3D_D3D\.dv|_decon)$')
    result = {}
    print '{'

    try:
        for path in paths:
            result.update(import_to_omero(path, pattern, ignores))
    except Exception, err:
        print >> sys.stderr, err

    print '}'
    #print json.dumps(result)

if __name__ == "__main__":
    main()
