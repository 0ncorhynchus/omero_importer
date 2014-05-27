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
    for path, dirs, files in os.walk(path):
        for file in files:
            if pattern is None or pattern.match(file):
                retval.append(os.path.join(path,file))
    return retval

def get_log(path):
    dirname = os.path.dirname(path)
    try:
        name, exp = os.path.basename(path).rsplit('.',1)
    except ValueError:
        raise

    logfile = ''
    if exp == 'dv_decon':
        logfile = dirname + '/' + name + '.dv.log'
    elif exp == 'dv':
        name = name.replace('_D3D','')
        logfile = dirname + '/' + name + '.dv.log'

    if not os.path.exists(logfile):
        raise IOError(errno.ENOENT, '', logfile)

    return logfile

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
    try:
        p = hikaridecon.run(path)
    except OSError, hikaridecon.DeconvoluteError:
        raise

    if p is None:
        return (None, False)
    p.wait()
    return (p, p.returncode == 0)

def update_error(obj, error, process):
    retval = {}.update(obj)
    retval['SUCCESS'] = False
    retval['ERROR'] = {}
    retval['ERROR']['TYPE'] = type(err).mro0()[0]
    retval['ERROR']['PROCESS'] = process
    retval['ERROR']['MESSAGE'] = err.message
    retval['ERROR']['STR'] = err.__str__()
    if hasattr(error, 'ice_name'):
        retval['ERROR']['ICE_NAME'] = error.ice_name
    return retval

processes = [('CONNECTING'), ('CHROMATIC SHIFT INIT'), ('LOG GETTING'),
    ('CHROMATIC SHIFT'), ('LOG WRITING'), ('IMPORTING')]

def import_file(path):
    retval = {}
    retval['PROCESSES'] = []

    if os.path.isdir(path) or not os.path.exists(path):
        return ({}, False)

    dirname = os.path.dirname(path)
    filename = os.path.basename(path)

    if ' ' in path:
        return ({}, False)

    uname = get_owner(path)
    if uname not in USERS:
        return ({}, False)

    passwd = USERS[uname]['PASSWORD']

    # CONNECTIONG
    retval['PROCESSES'].append('CONNECTING')
    try:
        conn = tools.connect_to_omero(uname, passwd)
    except (Ice.Exception, Exception), err:
        print >> sys.stderr, err
        retval_with_error = update_error(retval, err, retval['PROCESSES'][-1])
        return (retval_with_error, True)

    dataset = tools.get_dataset(conn, dirname)

    # CHROMATIC SHIFT INIT
    retval['PROCESSES'].append('CHROMATIC SHIFT INIT')
    try:
        zs = ChromaticShift(path)
    except (OSError, ValueError, ChromaticShiftError, Exception), err:
        print >> sys.stderr, err
        retval_with_error = update_error(retval, err, retval['PROCESSES'][-1])
        conn._closeSession()
        return (retval_with_error, True)

    existence = False
    if dataset is None:
        dataset = tools.create_dataset(conn, dirname)
    else:
        for image in dataset.listChildren():
            if image.getName() == zs.filename:
                existence = True
                break

    if existence:
        conn._closeSession()
        return ({}, False) # already exsited

    # LOG GETTING
    retval['PROCESSES'].append('LOG GETTING')
    try:
        log = get_log(path)
    except (ValueError, IOError, Exception), err:
        print >> sys.stderr, err
        retval_with_error = update_error(retval, err, retval['PROCESSES'][-1])
        conn._closeSession()
        return (retval, True)

    dest = '/omeroimports' + dirname + '/' + zs.filename
    image_uuid = str(uuid.uuid4())

    # CHROMATIC SHIFT
    retval['PROCESSES'].append('CHROMATIC SHIFT')
    try:
        zs.do()
        zs.move(dest)
    except (OSError, ChromaticShiftError, shutil.Error, Exception), err:
        print >> sys.stderr, err
        retval_with_error = update_error(retval, err, retval['PROCESSES'][-1])
        return (retval, True)

    # LOG WRITING
    retval['PROCESSES'].append('LOG WRITING')
    if not write_log(log, dest, image_uuid):
        retval_with_error = update_error(retval, err, retval['PROCESSES'][-1])
        conn._closeSession()
        return (retval, True)

    # IMPORTING
    retval['PROCESSES'].append('IMPORTING')
    import_args = ['/opt/omero445/importer-cli',
            '-s', 'localhost',
            '-u', uname,
            '-w', passwd,
            '-d', str(dataset.getId()),
            '-n', zs.filename, dest]
    import_prc = subprocess.Popen(import_args,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    import_prc.wait()
    if import_prc.returncode != 0:
        err_message = '\n'.join(import_prc.stderr.readlines())
        retval['SUCCESS'] = False
        retval['ERROR'] = {
                'TYPE': 'ImportingError',
                'PROCESS': 'IMPORTING',
                'STRERROR': err_message
                }
        conn._closeSession()
        return (retval, True)

    conn._closeSession()
    retval['SUCCESS'] = True
    return (retval, True)

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
            result[child] = obj
        elif not_shifted_pattern.match(child) and not os.path.exists(child + '_decon'):
            obj = {}
            obj['PROCESSES'].append('DECONVOLUTION')
            try:
                decon = deconvolute(child)
            except (OSError, Exception, hikaridecon.DeconvoluteError), err:
                print >> sys.stderr, err
                result[child] = update_error(err, {}, obj['PROCESSES'][-1])
                continue
            if decon[1]:
                obj, is_completed = import_file(decon[0].product_path)
                if not is_completed:
                    continue
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
    for path in paths:
        result.update(import_to_omero(path, pattern, ignores))
    print json.dumps(result)

if __name__ == "__main__":
    main()
