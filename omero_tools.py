import sys
try:
	from omero.gateway import BlitzGateway
	from omero.sys import ParametersI
	from omero import model
	from omero.rtypes import rstring
except:
	sys.stderr.write('You should run "source setup.sh" to added omero module to PYTHONPATH')
	sys.exit(1)

HOST = 'localhost'
PORT = 4064
def connect_to_omero(uname, passwd):
	conn = BlitzGateway(uname, passwd, host=HOST, port=PORT)
	connected = conn.connect()
	if not connected:
		sys.stderr.write("Error : Connection not available, please check your user name and password.\n")
		return None
	return conn

def get_dataset(conn, name):
	params = ParametersI()
	params.exp(conn.getUser().getId())
	datasets = conn.getObjects('Dataset', params=params)
	retval = None
	for dataset in datasets:
		if dataset.getName() == name:
			retval = dataset
			break
	return retval

def create_dataset(conn, name):
	dataset = model.DatasetI()
	dataset.setName(rstring(name))
	dataset = conn.getUpdateService().saveAndReturnObject(dataset)
	datasetId = dataset.getId().getValue()
	return conn.getObject("Dataset", datasetId)

def get_datasets(conn):
	params = ParametersI()
	params.exp(conn.getUser().getId())
	datasets = conn.getObjects('Dataset', params=params)
	return datasets

def get_images(conn):
	params=ParametersI()
	params.exp(conn.getUser().getId())
	images = conn.getObjects('Image', params=params)
	return images

