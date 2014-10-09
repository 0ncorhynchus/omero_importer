#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import shutil
import subprocess

class ChromaticShift:
    def __init__(self, path):
        self._filename = os.path.basename(path) + '.zs'
        self._origin = path
        args = ['/opt/bin/chromatic-shift', path]
        try:
            p = subprocess.Popen(args, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, shell=False)
            p.wait()
            if p.returncode != 0:
                raise ChromaticShiftError(1, '\n'.join(p.stderr.readlines()), path)
            self._commands = p.stdout.readlines()
        except (OSError, ValueError, ChromaticShiftError), err:
            raise

    def is_already_done(self, path=None):
        if path is None:
            path = self.path
        if not os.path.exists(path):
            return False
        shifted_stamp = os.stat(path).st_mtime
        origin_stamp = os.stat(self._origin).st_mtime
        return shifted_stamp > origin_stamp

    @property
    def path(self):
        return os.getcwd() + '/' + self._filename;

    @property
    def filename(self):
        return self._filename;

    def do(self):
        try:
            for cmd in self._commands:
                if cmd.lstrip().find('#') == 0:
                    continue
                prc = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
                prc.wait()
                if prc.returncode != 0:
                    raise ChromaticShiftError(2, '\n'.join(prc.stderr.readlines()), self._filename)
        except (OSError, ChromaticShiftError), err:
            raise

    def move(self, dest):
        if self.path == dest:
            return True
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        try:
            shutil.move(self.path, dest)
        except shutil.Error, err:
            raise
        return os.path.exists(dest)

class ChromaticShiftError(EnvironmentError):
    pass
