import os
import re

def search_dir(path):
	children = os.listdir(path)
	dirs = []
	for child in children:
		child = path + "/" + child
		if os.path.isdir(child):
			dirs.append(child)
			dirs.extend(search_dir(child))
	return dirs

def search_file(path, pattern=None):
	retval = []
	for child in os.listdir(path):
		child = os.path.join(path, child)
		if os.path.isfile(child):
			retval.append(child)
		if os.path.isdir(child):
			retval.extend(search_file(child))
	return retval
