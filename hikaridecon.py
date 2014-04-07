#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess
import re
import time

class HikariDecon:
    def __init__(self, jobcode, path):
        self._path = path
        self._returncode = 0
        self._jobcode = jobcode

    def wait(self):
        while True:
            time.sleep(0.1)
            p = subprocess.Popen(['hkrun', 'qstat', '-j %i'%self._jobcode],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            p.wait()
            if p.returncode != 0:
                break
        if os.path.exists(self._path + '_decon'):
            self._returncode = 0
        else:
            self._returncode = 1

    @property
    def returncode(self):
        return self._returncode

def run(path):
    p = subprocess.Popen(['hikaridecon', path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    p.wait()
    if p.returncode != 0:
        print >> sys.stderr
        return None

    outputs = p.stdout.readlines()
    pattern = re.compile('^Your job ([0-9]*)(.*)')
    jobcode = -1
    for line in outputs:
        match = pattern.match(line)
        if match:
            jobcode = int(match.group(1))
            break
    if jobcode == -1:
        return None

    retval = HikariDecon(jobcode, path)
    return retval

