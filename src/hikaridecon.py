#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import re
import time
import errno
from distutils.spawn import find_executable

class HikariDecon:
    def __init__(self, jobcode, path):
        self._path = path
        self._returncode = 0
        self._stderr = ''
        self._jobcode = jobcode

    def wait(self):
        while True:
            time.sleep(0.1)
            try:
                p = subprocess.Popen(['hkrun', 'qstat', '-j %i'%self._jobcode],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
                p.wait()
            except OSError, e:
                self._returncode = 2
                raise
            if p.returncode != 0:
                break
        if os.path.exists(self._path + '_decon'):
            self._returncode = 0
        else:
            self._stderr = 'The deconvoluted file is not found.'
            self._returncode = 1

    @property
    def product_path(self):
        return self._path + '_decon'

    @property
    def returncode(self):
        return self._returncode

    @property
    def stderr(self):
        return self._stderr

def check_size(path, max_size):
    filesize = os.path.getsize(path)
    return (filesize, filesize <= max_size)

def alert_size(path, max_size):
    filesize, flg = check_size(path, max_size)
    if not flg:
        size_gb = filesize / 1024 / 1024 / 1024
        raise DeconvoluteError(errno.EFBIG,
                'File size %d Gb is over 2Gb' % size_gb, path)

def run(path):
    cwd = os.getcwd()
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)

    alert_size(path, 2 * 1024 * 1024 * 1024)

    hikaridecon = 'hikaridecon'
    os.chdir(dirname)
    if not find_executable(hikaridecon):
        raise DeconvoluteError(0,
                '\'%s\' is not executable.' % hikaridecon)
    try:
        p = subprocess.Popen([hikaridecon, basename],
                stdout=subprocess.PIPE, shell=False)
        p.wait()
    except OSError, e:
        raise

    os.chdir(cwd)
    if p.returncode != 0:
        raise DeconvoluteError(p.returncode,
                '\n'.join(p.stderr.readlines()), path)

    outputs = p.stdout.readlines()
    pattern = re.compile('^Your job ([0-9]*)(.*)')
    jobcode = -1
    for line in outputs:
        match = pattern.match(line)
        if match:
            jobcode = int(match.group(1))
            break
    if jobcode == -1:
        raise DeconvoluteError(errno.ENOMSG,
                'Cannot get any jobcode', path)

    retval = HikariDecon(jobcode, path)
    return retval

class DeconvoluteError(EnvironmentError):
    pass
