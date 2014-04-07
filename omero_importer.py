#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import errno
import shutil
import re
import uuid
import subprocess

import omero_tools
import setlog
from chromaticshift import ChromaticShift
from data import users
from imagefile import ImageFile

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
    for uname in users:
        for keyword in users[uname]['keywords']:
            if keyword in path:
                return uname

    for uname in users:
        if uid in users[uname]['uids']:
            return uname

    return None

def import_file(path):
    if os.path.isdir(path):
        return False
    if not os.path.exists(path):
        return False

    dirname = os.path.dirname(path)
    filename = os.path.basename(path)

    uname = get_owner(path)
    if uname not in users:
        print >> sys.stderr, 'the owner of %s is not found.\n' % path
        return False
    passwd = users[uname]['passwd']

    conn = omero_tools.connect_to_omero(uname, passwd)
    dataset = omero_tools.get_dataset(conn, dirname)

    print '#' * 50
    print '[import_file] %s' % path
    if ' ' in path:
        print '%s includes the space \' \'.' % path
        conn._closeSession()
        return False

    try:
        zs = ChromaticShift(path)
    except (OSError, ValueError, ChromaticShiftError), err:
        print >> sys.stderr, err
        conn._closeSession()
        return False

    existence = False
    if dataset is None:
        dataset = omero_tools.create_dataset(conn, dirname)
    else:
        for image in dataset.listChildren():
            if image.getName() == zs.filename:
                print '%s exists.' % zs.filename
                existence = True
                break

    if existence:
        conn._closeSession()
        return False

    try:
        log = get_log(path)
    except (ValueError, IOError), err:
        print >> sys.stderr, err
        conn._closeSession()
        return False

    print '[log] %s' % log
    dest = '/omeroimports' + dirname + '/' + zs.filename
    print '[dest] %s' % dest
    image_uuid = str(uuid.uuid4())
    print '[uuid] %s' % image_uuid
    # chromatic shift
    try:
        zs.do()
        zs.move(dest)
    except (OSError, ChromaticShiftError), err:
        print >> sys.stderr, err
        conn._closeSession()
        return False
    except shutil.Error, err:
        print >> sys.stderr, err
        conn._closeSession()
        return False

    # set log
    if not setlog.write_log(log, dest, image_uuid):
        print >> sys.stderr, 'Can\'t write logs into %s' % dest
        conn._closeSession()
        return False

    # import
    import_args = ['/opt/omero445/importer-cli',
            '-s', 'localhost',
            '-u', uname,
            '-w', passwd,
            '-d', str(dataset.getId()),
            '-n', zs.filename, dest]
    import_prc = subprocess.Popen(import_args,
            stderr=subprocess.PIPE, shell=False)
    import_prc.wait()
    if import_prc.returncode != 0:
        print >> sys.stderr, '\n'.join(import_prc.stderr.readlines())
        conn._closeSession()
        return False

    conn._closeSession()
    return True

def import_to_omero(path, pattern=None, ignores=None):
    hidden_pattern = re.compile('^\..*')
    try:
        children = os.listdir(path)
    except:
        return

    for child in children:
        if hidden_pattern.match(child):
            continue
        child = os.path.join(path, child)
        if ignores is not None and child in ignores:
            continue
        if not os.access(child, os.R_OK):
            continue
        if pattern is None or pattern.match(child):
            import_file(child)
        if os.path.isdir(child):
            import_to_omero(child, pattern, ignores)

def main():
    argv = sys.argv
    argc = len(argv)

    if argc == 1:
        paths = ['/data2', '/data3', '/data5']
    else:
        paths = argv

    ignores = ['/data5/data3_backup_20130819', '/data5/suguru/omero-imports']
    pattern = re.compile('(.*)_decon$')
    # only import files deconvoluted with hikaridecon
    #pattern = re.compile('(.*)(R3D_D3D\.dv|_decon)$')
    for path in paths:
        import_to_omero(path, pattern, ignores)

if __name__ == "__main__":
    main()
