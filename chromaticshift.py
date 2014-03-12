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
			p = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False)
			self._commands = p.stdout.readlines()
		except OSError:
			print >> sys.stderr, 'Error'

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
				prc = subprocess.Popen(cmd, shell=True)
				prc.wait()
		except OSError:
			print >> sys.stderr, 'Error: can\'t execute commands'

	def move(self, dest):
		dest_dir = os.path.dirname(dest)
		if not os.path.exists(dest_dir):
			os.makedirs(dest_dir)
		try:
			shutil.move(self.path, dest)
		except shutil.Error:
			print >> sys.stderr, 'Can\'t move %s to %s' % (self.path, dest)
		return os.path.exists(dest)
