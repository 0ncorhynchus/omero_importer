#! /usr/bin/python
import sys
import os
import shutil
import re
import uuid
import subprocess
import omero_tools
import setlog

users = {
		'asato': {
			'passwd': 'omx',
			'uids': (10104,),
			'keywords': ('aya',)
			},
		'gkafer': {
			'passwd': 'omx',
			'uids': (511,),
			'keywords': ('Georgia', 'gkafer')
			},
		'klu': {
			'passwd': 'omx',
			'uids': (508,),
			'keywords': ('klu', 'kai')
			},
		'rrillo': {
			'passwd': 'omx',
			'uids': (509,),
			'keywords': ('regina',)
			},
		'suguru': {
			'passwd': 'omx',
			'uids': (1002,),
			'keywords': ('suguru',)
			},
		'xli': {
			'passwd': 'omx',
			'uids': (510,),
			'keywords': ('xuan',)
			}
		}

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
			sys.stderr.write('Error: can\'t execute commands')

	def move(self, dest):
		dest_dir = os.path.dirname(dest)
		if not os.path.exists(dest_dir):
			os.makedirs(dest_dir)
		try:
			shutil.move(self.path, dest)
		except shutil.Error:
			sys.stderr.write('Can\'t move %s to %s' % (self.path, dest))
		return os.path.exists(dest)

def getLog(path):
	dirname = os.path.dirname(path)
	name, exp = os.path.basename(path).rsplit('.',1)
	logfile = ''
	if exp == 'dv_decon':
		logfile = dirname + '/' + name + '.dv.log'
	elif exp == 'dv':
		name = name.replace('_D3D','')
		logfile = dirname + '/' + name + '.dv.log'

	if not os.path.exists(logfile):
		logfile = None
	return logfile

def getOwner(path):
	uid = os.stat(path).st_uid
	for uname in users:
		if uid in users[uname]['uids']:
			return uname

	for uname in users:
		for keyword in users[uname]['keywords']:
			if keyword in path:
				return uname
	
	return None

def import_file(path):
	dirname = os.path.dirname(path)
	filename = os.path.basename(path)

	uname = getOwner(path)
	if uname not in users:
		sys.stderr.write('the owner of %s is not found.\n' % path)
		return
	passwd = users[uname]['passwd']

	conn = omero_tools.connect_to_omero(uname, passwd)
	dataset = omero_tools.get_dataset(conn, dirname)

	print '#' * 50
	print '[import_file] %s' % path
	zs = ChromaticShift(path)
	existence = False
	if dataset is None:
		dataset = omero_tools.create_dataset(conn, dirname)
	else:
		for image in dataset.listChildren():
			if image.getName() == zs.filename:
				print '%s exists.' % zs.filename
				existence = True
				break
	if not existence:
		log = getLog(path)
		if log is not None:
			print '[log] %s' % log
			dest = '/omeroimports' + dirname + '/' + zs.filename
			print '[dest] %s' % dest
			image_uuid = str(uuid.uuid4())
			print '[uuid] %s' % image_uuid
			# chromatic shift
			zs.do()
			if not os.path.exists(zs.path):
				sys.stderr.write('%s does not exist.' % zs.path)
				conn._closeSession()
				return
			if not zs.move(dest):
				sys.stderr.write('Can\'t move %s to %s' % (self.path, dest))
				conn._closeSession()

			# set log
			if not setlog.write_log(log, dest, image_uuid):
				sys.stderr.write('Can\'t write logs into %s' % dest)
				conn._closeSession()

			# import
			import_args = ['/opt/omero445/importer-cli',
					'-s', 'localhost',
					'-u', uname,
					'-w', passwd,
					'-d', str(dataset.getId()),
					'-n', zs.filename, dest]
			import_prc = subprocess.Popen(import_args,
					shell=False)
			import_prc.wait()
	conn._closeSession()

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
	paths = ['/data1', '/data2']
	ignores = ['/data5/data3_backup_20130819', '/data5/suguru/omero-imports']
	pattern = re.compile('(.*)(R3D_D3D\.dv|_decon)$')
	for path in paths:
		import_to_omero(path, pattern, ignores)

if __name__ == "__main__":
	main()
