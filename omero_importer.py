#! /usr/bin/python
import sys
import os
import re
import uuid
import subprocess
import omero_tools
import setlog

# uid : (account, passwd)
users = {508: ('klu', 'omx'),
		509: ('rrillo', 'omx'),
		510: ('xli', 'omx'),
		511: ('gkafer', 'omx'),
		1002: ('suguru', 'omx'),
		10104: ('asato', 'omx')}
"""
uid: uname
{0: 'root',
 502: '----',
 1000: 'pcarlton',
 1002: 'suguru',
 10102: 'ayasato',
 10104: '----',
 508: 'klu',
 509: 'rrillo',
 510: 'xli',
 511: 'gkafer'}
"""

pattern = re.compile('(.*)(R3D_D3D\.dv|_decon)$')
hidden_pattern = re.compile('^\..*')

def search_files(path, pattern=None):
	retval = []
	for path, dirs, files in os.walk(path):
		for file in files:
			if pattern is None or pattern.match(file):
				retval.append(os.path.join(path,file))
	return retval

class ChromaticShift:
	def __init__(self, path):
		self._filename = os.path.basename(path) + '.zs'
		args = ['/opt/bin/chromatic-shift', path]
		try:
			p = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False)
			self._commands = p.stdout.readlines()
		except OSError:
			sys.stderr.write('Error')

	@property
	def path(self):
		return '/tmp/' + self._filename;

	@property
	def filename(self):
		return self._filename;

	def do(self):
		try:
			for cmd in self._commands:
				if cmd.find('#') == 0:
					continue
				subprocess.call(cmd, shell=True)
		except OSError:
			sys.stderr.write('Error: can\'t execute commands')

	def move(self, dest):
		try:
			subprocess.call(['mv', self.path, dest], shell=False)
		except OSError:
			sys.stderr.write('Can\'t move %s to %s' % (self.path, dest))

def getLog(path):
	dirname = os.path.dirname(path)
	name, exp = os.path.basename(path).rsplit('.',1)
	logfile = ''
	if exp == 'dv' or exp == 'dv_decon':
		logfile = dirname + '/' + name + '.dv.log'
	if not os.path.exists(logfile):
		logfile = ''
	return logfile

def import_file(path):
	dirname = os.path.dirname(path)
	filename = os.path.basename(path)
	uid = os.stat(path).st_uid
	if uid not in users:
		sys.stderr.write('uid %d is unknown\n' % uid)
		return
	uname, passwd = users[uid]
	conn = omero_tools.connect_to_omero(uname, passwd)
	dataset = omero_tools.get_dataset(conn, dirname)
	print '#' * 50
	print '[import_file] %s' % path
	zs = ChromaticShift(path)
	if dataset is not None:
		existence = False
		for image in dataset.listChildren():
			if image.getName() == zs.filename:
				print '%s exists.' % zs.filename
				existence = True
				break
		if not existence:
			log = getLog(path)
			if log != '':
				print '[log] %s' % log
				dest = '/omeroimports' + dirname + '/' + zs.filename
				print '[dest] %s' % dest
				image_uuid = str(uuid.uuid4())
				print '[uuid] %s' % image_uuid
				zs.do()
				zs.move(dest)
				# set log
				setlog.write_log(log, dest, image_uuid)
				# import
				import_args = ['/opt/omero445/importer-cli',
						'-s', 'localhost',
						'-u', uname,
						'-w', passwd,
						'-d', str(dataset.getId()),
						'-n', zs.filename,
						dest]
				import_prc = subprocess.Popen(import_args,
						shell=False)
				import_prc.wait()
	conn._closeSession()

def import_to_omero(path, pattern=None):
	try:
		children = os.listdir(path)
	except:
		return

	for child in children:
		if hidden_pattern.match(child):
			continue
		child = os.path.join(path, child)
		if not os.access(child, os.R_OK):
			continue
		if pattern is None or pattern.match(child):
			import_file(child)
		if os.path.isdir(child):
			import_to_omero(child, pattern)

def main():
	paths = ['/data1']
	for path in paths:
		import_to_omero(path, pattern)

if __name__ == "__main__":
	main()
