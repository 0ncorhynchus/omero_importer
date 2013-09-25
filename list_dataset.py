HOST = 'localhost'
PORT = 4064
USERNAME = 'asato'
PASSWORD = 'omx'

from omero.gateway import BlitzGateway
from omero.sys import ParametersI
import os.path

def connect_to_omero():
	conn = BlitzGateway(USERNAME, PASSWORD, host=HOST, port=PORT)
	connected = conn.connect()
	if not connected:
		import sys
		sys.stderr.write("Error : Connection not available, please check your user name and password.\n")
		return None
	return conn

def list_datasets(conn):
	print "\nList Datasets:"
	print "="*50
	params = ParametersI()
	params.exp(conn.getUser().getId())
	datasets = conn.getObjects("Dataset", params=params)
	for dataset in datasets:
		print "+Dataset: %s(%s)" % (
				dataset.getName(), dataset.getId())
		for image in dataset.listChildren():
			print "|-Image: %s(%s)" % (
					image.getName(), image.getId())

def main():
	conn = connect_to_omero()
	list_datasets(conn)
	conn._closeSession()

if __name__ == "__main__":
	main()
