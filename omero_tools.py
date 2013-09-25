
import sys
try:
	from omero.gateway import BlitzGateway
	from omero.sys import ParametersI
	from omero import model
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

def get_dataset(conn, dname):
	params = ParametersI()
	params.exp(conn.getUser().getId())
	datasets = conn.getObjects('Dataset', params=params)
	datasetId = -1
	retval = None
	for dataset in datasets:
		if dataset.getName() == dname:
			retval = dataset
			break
	return retval
	if retval is None:
		retval = model.DatasetI()
		retval.setName(rstring(dname))
		retval = conn.getUpdateService().saveAndReturnObject(retval)
	return datasetId

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

