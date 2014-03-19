#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import shutil
import subprocess

class ChromaticShift:
    def __init__(self, path):
        self._filename = os.path.basename(path) + '.zs'
        args = ['/opt/bin/chromatic-shift', path]
        try:
            p = subprocess.Popen(args, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, shell=False)
            p.wait()
            if p.returncode != 0:
                raise ChromaticShiftError('\n'.join(p.stderr.readlines()))
            self._commands = p.stdout.readlines()
        except (OSError, ValueError, ChromaticShiftError), err:
            #print >> sys.stderr, err
            raise

    @property
    def path(self):
        return os.getcwd() + '/' + self._filename;

    @property
    def filename(self):
        return self._filename;

    def do(self):
        try:
            for cmd in self._commands:
                if cmd.find('#') == 0:
                    continue
                prc = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
                prc.wait()
                if prc.returncode != 0:
                    raise ChromaticShiftError('\n'.join(prc.stderr.readlines()))
        except (OSError, ChromaticShiftError), err:
            #print >> sys.stderr, err
            raise

    def move(self, dest):
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        try:
            shutil.move(self.path, dest)
        except shutil.Error, err:
            #print >> sys.stderr, err
            raise
        return os.path.exists(dest)

class ChromaticShiftError(EnvironmentError):
    pass
