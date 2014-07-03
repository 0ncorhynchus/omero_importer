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
from copy import deepcopy

from settings import *
from omero_import import *
import Ice

def search_files(path, pattern=None):
    retval = []
    for dpath, dirs, files in os.walk(path):
        for file in files:
            if pattern is None or pattern.match(file):
                retval.append(os.path.join(dpath,file))
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

def update_error(obj, error, prcname):
    retval = deepcopy(obj)
    retval['SUCCESS'] = False
    retval['ERROR'] = {}
    retval['ERROR']['TYPE'] = str(type(error).mro()[0])
    retval['ERROR']['PROCESS'] = prcname
    retval['ERROR']['MESSAGE'] = error.message
    retval['ERROR']['STR'] = error.__str__()
    if hasattr(error, 'ice_name'):
        retval['ERROR']['ICE_NAME'] = error.ice_name
    return retval

getPassword = lambda uname: USERS[uname]['PASSWORD']

def connect(obj):
    new_obj = deepcopy(obj)
    new_obj['conn'] = tools.connect_to_omero(obj['uname'], obj['passwd'])
    new_obj['dataset'] = tools.get_dataset(obj['conn'], obj['dirname'])
    return new_obj

def init_chromatic_shift(obj):
    new_obj = deepcopy(obj)
    new_obj['zs'] = ChromaticShift(obj['path'])
    return new_obj

def check_not_imported_yet(obj):
    imported = False
    if obj['dataset'] is None:
        obj['dataset'] = tools.create_dataset(conn, dirname)
    else:
        for image in obj['dataset'].listChildren():
            if image.getName() == obj['zs'].filename:
                imported = True
                break
    if imported:
        fail(EnvironmentError, '%s is already imported.' % obj['path'])
    return obj

def get_log(obj):
    '''
    argument: a file path
    return: the log file path
    can raise ValueError, IOError
    '''

    path = obj['path']
    dirname = os.path.dirname(path)
    name, exp = os.path.basename(path).rsplit('.',1)

    new_obj = deepcopy(obj)

    logfile = ''
    if exp == 'dv_decon':
        logfile = dirname + '/' + name + '.dv.log'
    elif exp == 'dv':
        name = name.replace('_D3D','')
        logfile = ''.join([dirname, '/', name, '.dv.log'])

    if not os.path.exists(logfile):
        fail(IOError, errno.ENOENT, '', logfile)

    new_obj['logfile'] = logfile
    new_obj['dest'] = ''.join('/omeroimports', obj['dirname'], '/', obj['zs'].filename)
    new_obj['image_uuid'] = str(uuid.uuid4())

    return new_obj

def run_chromatic_shift(obj):
    new_obj = deepcopy(obj)
    new_obj['zs'].do()
    new_obj['zs'].move(obj['dest'])
    return new_obj

def add_log(obj):
    obj['retval']['PROCESSES'].append('LOG WRITING')
    if not write_log(obj['logfile'], obj['dest'], obj['image_uuid']):
        fail(EnvironmentError, '%s can not be written to %s.' % (obj['logfile'], obj['dest']))

def import_main(obj):
    args = ['/opt/omero445/importer-cli',
            '-s', 'localhost',
            '-u', obj['uname'],
            '-w', obj['passwd'],
            '-d', str(dataset.getId()),
            '-n', zs.filename, dest]
    import_prc = subprocess.Popen(args, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=False)
    import_prc.wait()
    if import_prc.returncode != 0:
        err_message = '\n'.join(import_prc.stderr.readlines())
        fail(EnvironmentError, err_message)

def unit_process(prcname, func, obj):
    obj['retval']['PROCESS'].append(prcname)
    try:
        new_obj = func(obj)
    except Exception, err:
        retval = obj['retval']
        obj['retval'] = update_error(retval, er, prcname)
        raise
    return new_obj

def import_file(path):
    ns = {'retval':{'PROCESSES': []}}
    ns['path'] = path

    if os.path.isdir(path) or not os.path.exists(path):
        return ({}, False)

    if ' ' in path:
        return ({}, False)

    ns['dirname'] = os.path.dirname(path)
    ns['filename'] = os.path.basename(path)

    ns['uname'] = get_owner(path)
    if uname not in USERS:
        return ({}, False)

    ns['passwd'] = getPassword(uname)

    try:
        ns = reduce(lambda obj, fun: fun(obj), [
            partial(partial(unit_process, 'CONNECTING'), connect),
            partial(partial(unit_process, 'CHROMATIC SHIFT INIT'), init_chromatic_shift)
            partial(partial(unit_process, 'CHECKING NOT IMIPORTED YET'), check_not_imported_yet),
            partial(partial(unit_process, 'LOG GETTING'), get_log),
            partial(partial(unit_process, 'CHROMATIC SHIFT RUNNING'), run_chromatic_shift),
            partial(partial(unit_process, 'LOG WRITING'), add_log)
            partial(partial(unit_process, 'IMPORTING'), import_main)
            ], ns)
    except Exception, err:
        print >> sys.stderr, err
        if 'conn' in ns and ns['conn'].connect():
            ns['conn']._closeSession()
        return (ns['retval'], True)

    ns['conn']._closeSession()
    ns['retval']['SUCCESS'] = True
    return (ns['retval'], True)

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
        child = os.path.join(path, child)
        if ignores is not None and child in ignores:
            continue
        if not os.access(child, os.R_OK):
            continue

        if os.path.isdir(child):
            result.update(import_to_omero(child, pattern, ignores))
        elif pattern is None or pattern.match(child):
            obj, is_completed = import_file(child)
            if not is_completed:
                continue
            #result[child] = obj
            print '"%s": %s' % (path, json.dumps(obj))
        elif not_shifted_pattern.match(child) and not os.path.exists(child + '_decon'):
            obj = {}
            obj['PROCESSES'] = ['DECONVOLUTION']
            try:
                decon, is_succeeded = deconvolute(child)
            except (OSError, Exception, hikaridecon.DeconvoluteError), err:
                print >> sys.stderr, err
                result[child] = update_error({}, err, obj['PROCESSES'][-1])
                continue
            if is_succeeded:
                obj, is_completed = import_file(decon.product_path)
                if not is_completed:
                    continue
                #result[child] = obj
                print '"%s": %s' % (path, json.dumps(obj))
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
