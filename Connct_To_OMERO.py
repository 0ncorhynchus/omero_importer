HOST = 'localhost'
PORT = 4064
USERNAME = 'suguru'
PASSWORD = 'omx'

from omero.gateway import BlitzGateway
from omero.sys import ParametersI

def connect_to_omero():
	conn = BlitzGateway(USERNAME, PASSWORD, host=HOST, port=PORT)
	connected = conn.connect()
	if not connected:
		import sys
		sys.stderr.write("Error : Connection not available, please check your user name and password.\n")
		return None
	return conn

def print_obj(obj, indent=0):
	print """%s%s:%s Name:"%s" (owner=%s)""" % (\
			" " * indent,\
			obj.OMERO_CLASS,\
			obj.getId(),\
			obj.getName(),\
			obj.getOwnerOmeName())

def read_user_info(conn):
	user = conn.getUser()
	print "Current user:"
	print "\tID:", user.getId()
	print "\tUsername:", user.getName()
	print "\tFull Name':", user.getFullName()

	print "Member of:"
	for g in conn.getGroupsMemberOf():
		print "\tID:", g.getId(), " Name:", g.getName()
	group = conn.getGroupFromContext()
	print "Current group: ", group.getName()

	print "Other Membera of current group:"
	for exp in conn.listColleagues():
		print "\tID:", exp.getId(), exp.getOmeName(), " Name:", exp.getFullName()

	print "Owner of:"
	for g in conn.listOwnedGroups():
		print "\tID:", g.getId(), " Name:", g.getName()

def read_data(conn):
	imageId = 9
	datasetId = 2
	plateId = -1

	print "\nList Projects:"
	print "=" * 50
	my_expId = conn.getUser().getId()
	for project in conn.listProjects(my_expId):
		print_obj(project)
		for dataset in project.listChildren():
			print_obj(dataset, 2)
			for image in dataset.listChildren():
				print_obj(image, 4)

	print "\nList Datasets:"
	print "=" * 50
	params = ParametersI()
	params.exp(conn.getUser().getId())
	datasets = conn.getObjects("Dataset", params=params)
	for dataset in datasets:
		print_obj(dataset)

	print "\nDataset:%s" % datasetId
	print "=" * 50
	dataset = conn.getObject("Dataset", datasetId)
	print "\nImages in Dataset:", dataset.getName()
	for image in dataset.listChildren():
		print_obj(image)

	image = conn.getObject("Image", imageId)
	print "\nImage:%s" % imageId
	print "=" * 50
	print image.getName(), image.getDescription()
	#Retrieve information about an image
	print "X:", image.getSizeX()
	print "Y:", image.getSizeY()
	print "Z:", image.getSizeZ()
	print "C:", image.getSizeC()
	print "T:", image.getSizeT()
	#render the first timepoint, mid Z section
	z = image.getSizeZ() / 2
	t = 0
	renderedImage = image.renderImage(z, t)
	#renderedImage.show() #popup (use for debug only)
	#renderedImage.save("test.jpg") #save in the currend folder

	print "\nList Screens:"
	print "=" * 50
	for screen in conn.getObjects("Screen"):
		print_obj(screen)
		for plate in screenlistChildren():
			print_obj(plate, 2)
			plateId = plate.getId()

			if plateId >= 0:
				print "\nPlate:%s" % plateId
				print "=" * 50
				plate = conn.getObject("Plate", plateid)
				print "\nNumber ob fields:", plate.getNumberOfFields()
				print "\nGrid size:", plate.getGridSize()
				print "\n Wells in Plate:", plate.getName()
				for well in plate.listChildren():
					index = well.countWellSample()
					print " Well: ", well.row, well.column, " Fields:", index
					for index in xrange(0, index):
						print "  Image: ", \
								well.getImage(index).getName(), \
								well.getImage(index).getId()

def read_groups(conn):
	imageId = 9
	group = conn.getGroupFromContext()
	print "Current group:", group.getName()

	group_perms = group.getDetails().getPermissions()
	perm_string = str(group_perms)
	permission_names = {'rw----':'PRIVATE',
			'rwr---':'READ-ONLY',
			'rwra--':'READ-ANNOTATE',
			'rwrw--':'REAAD-WRITE'}
	print "Permissions: %s(%s)" % (permission_names[perm_string], perm_string)

	projects = conn.listProjects()
	for p in projects:
		print p.getName(), "Owner: ", p.getDetails().getOwner().getFullName()

	image = conn.getObject("Image", imageId)
	print "Image: ", image

	groupId = image.details.group.id.val
	conn.SERVICE_OPTS.setOmeroGroup(groupId)
	projects = conn.listProjects()
	image = conn.getObject("Image", imageId)
	print "Image: ", image,

def access_to_raw_data(conn):
	imageId = 3358
	image = conn.getObject("Image", imageId)
	sizeZ = image.getSizeZ()
	sizeC = image.getSizeC()
	sizeT = image.getSizeT()
	z, t, c = 0, 0, 0
	pixels = image.getPrimaryPixels()
	plane = pixels.getPlane(z, c, t)
	print "\nPlane at zct: ", z, c, t
	print plane
	print "shape: ", plane.shape
	print "min:", plane.min(), "max:", plane.max(),\
			"pixel type:", plane.dtype.name

	c, t = 0, 0
	tile = (50, 50, 10, 10)
	zctList = [(z, c, t, tile) for z in range(sizeZ)]
	print "\nZ stack of tiles:"
	planes = pixels.getTiles(zctList)
	for i, p in enumerate(planes):
		print "Tile:", zctList[i], " min:", p.min(), \
				" max:", p.max(), " sum:",p.sum()

	zctList = []
	for z in range(sizeZ / 2, sizeZ):
		for c in range(sizeC):
			for t in range(sizeT):
				zctList.append((z, c, t))
	print "\nHyper stack of planes:"
	planes = pixels.getPlanes(zctList)
	for i, p in enumerate(planes):
		print "plane zct:", zctList[i], " min:", p.min(), " max:", p.max()

if __name__ == '__main__':

	conn = connect_to_omero()
	if conn is None:
		sys.exit(1)

	read_user_info(conn)
	read_data(conn)
	read_groups(conn)
	access_to_raw_data(conn)

	ctx = conn.getEventContext()
	conn._closeSession()

