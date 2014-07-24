#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import re
import time
import errno

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

def run(path):
    pwd = os.getcwd()
    dirname = os.path.dirname(path)
    filesize = os.path.getsize(path)

    if filesize >= 2 * 1024 * 1024 * 1024:
        size_gigabyte = filesize / 1024 / 1024 / 1024
        raise DeconvoluteError(errno.EFBIG,
                'File size %d Gb is over 2Gb' % size_gigabyte, path)

    basename = os.path.basename(path)
    os.chdir(dirname)
    try:
        p = subprocess.Popen(['hikaridecon', basename],
                stdout=subprocess.PIPE, shell=False)
        p.wait()
    except OSError, e:
        raise

    os.chdir(pwd)
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
