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

def search_files(path, pattern=None):
    retval = []
    for dpath, dirs, files in os.walk(path):
        if pattern is not None:
            files = filter(lambda f: pattern.match(f), files)
        retval = concat(retval, map(lambda f: os.path.join(dpath, f), files))
    return retval

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

def deconvolute(path):
    '''
    argument: a file path
    return: a tuple (a Popen instance, success flag)
    can raise OSError, hikaridecon.DeconvoluteError
    '''
    p = hikaridecon.run(path)
    if p is None:
        return (None, False)
    p.wait()
    return (p, p.returncode == 0)

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

getPassword = lambda uname: USERS[uname]['PASSWORD']

def connect(**kwargs):
    kwargs['conn'] = tools.connect_to_omero(kwargs['uname'], kwargs['passwd'])
    kwargs['dataset'] = tools.get_dataset(kwargs['conn'], kwargs['dirname'])
    return kwargs

def init_chromatic_shift(**kwargs):
    kwargs['zs'] = ChromaticShift(kwargs['path'])
    return kwargs

def check_not_imported_yet(**kwargs):
    imported = False
    if kwargs['dataset'] is None:
        kwargs['dataset'] = tools.create_dataset(kwargs['conn'], kwargs['dirname'])
    else:
        for image in kwargs['dataset'].listChildren():
            if image.getName() == kwargs['zs'].filename:
                imported = True
                break
    if imported:
        fail(EnvironmentError, errno.EEXIST,
                '%s is already imported.' % kwargs['path'], kwargs['path'])
    return kwargs

def get_log(**kwargs):
    '''
    argument: a file path
    return: the log file path
    can raise ValueError, IOError
    '''

    path = kwargs['path']
    dirname = os.path.dirname(path)
    name, exp = os.path.basename(path).rsplit('.',1)

    logfile = ''
    if exp == 'dv_decon':
        logfile = dirname + '/' + name + '.dv.log'
    elif exp == 'dv':
        name = name.replace('_D3D','')
        logfile = ''.join([dirname, '/', name, '.dv.log'])

    if not os.path.exists(logfile):
        fail(IOError, errno.ENOENT, 'a logfile %s does not exist.' % logfile, logfile)

    kwargs['logfile'] = logfile
    kwargs['dest'] = ''.join(['/omeroimports', kwargs['dirname'], '/', kwargs['zs'].filename])
    kwargs['image_uuid'] = str(uuid.uuid4())

    return kwargs

def run_chromatic_shift(**kwargs):
    kwargs['zs'].do()
    kwargs['zs'].move(kwargs['dest'])
    return kwargs

def add_log(**kwargs):
    kwargs['retval']['PROCESSES'].append('LOG WRITING')
    if not write_log(kwargs['logfile'], kwargs['dest'], kwargs['image_uuid']):
        fail(IOError, errno.EIO,
                '%s can not be written to %s.' % (kwargs['logfile'], kwargs['dest']))
    return kwargs

def import_main(**kwargs):
    args = ['/opt/omero445/importer-cli',
            '-s', 'localhost',
            '-u', kwargs['uname'],
            '-w', kwargs['passwd'],
            '-d', str(kwargs['dataset'].getId()),
            '-n', kwargs['zs'].filename, kwargs['dest']]
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
    if 'conn' in kwargs:
        kwargs['conn'].seppuku(softclose=True)

def import_file(path):
    kwargs = {'retval':{'PROCESSES': []}}
    kwargs['path'] = path

    if os.path.isdir(path) or not os.path.exists(path):
        return ({}, False)

    if ' ' in path:
        return ({}, False)

    kwargs['dirname'] = os.path.dirname(path)
    kwargs['filename'] = os.path.basename(path)

    kwargs['uname'] = get_owner(path)
    if kwargs['uname'] not in USERS:
        return ({}, False)

    kwargs['passwd'] = getPassword(kwargs['uname'])

    try:
        kwargs = reduce(lambda obj, fun: fun(**obj), [
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

    close_session(**kwargs)
    return (kwargs['retval'], True)

def import_to_omero(path, pattern=None, ignores=None):
    hidden_pattern = re.compile('^\..*')
    not_shifted_pattern = re.compile('(.*)R3D.dv$')
    try:
        children = os.listdir(path)
    except:
        return {}

    result = {}
    for child in children:
        if hidden_pattern.match(child):
            continue
        fullpath = os.path.join(path, child)
        if ignores is not None and fullpath in ignores:
            continue
        if not os.access(fullpath, os.R_OK):
            continue

        if os.path.isdir(fullpath):
            result.update(import_to_omero(fullpath, pattern, ignores))
        elif pattern is None or pattern.match(fullpath):
            obj, is_completed = import_file(fullpath)
            if not is_completed:
                continue
            #result[fullpath] = obj
            if 'ERROR' not in obj or  'ERRNO' not in obj['ERROR'] or obj['ERROR']['ERRNO'] != errno.EEXIST:
                print '"%s": %s' % (fullpath, json.dumps(obj))
        elif not_shifted_pattern.match(fullpath) and not os.path.exists(fullpath + '_decon'):
            obj = {}
            obj['PROCESSES'] = ['DECONVOLUTION']
            try:
                decon, is_succeeded = deconvolute(fullpath)
            except (OSError, Exception, hikaridecon.DeconvoluteError), err:
                print >> sys.stderr, err
                update_error(result[fullpath], err, 'DECONVOLUTION')
                continue
            if is_succeeded:
                obj, is_completed = import_file(decon.product_path)
                if not is_completed:
                    continue
                #result[fullpath] = obj
                if 'ERROR' not in obj or 'ERRNO' not in obj['ERROR'] or obj['ERROR']['ERRNO'] != errno.EEXIST:
                    print '"%s": %s' % (fullpath, json.dumps(obj))
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
    pattern = re.compile('(.*)_decon$')
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
