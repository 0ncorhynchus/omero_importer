import re
import omero_tools

users = (
		('klu', 'omx'),
		('rrillo', 'omx'),
		('xli', 'omx'),
		('gkafer', 'omx'),
		('suguru', 'omx'),
		('asato', 'omx')
		)
def main():
	pattern = re.compile('^(.*)\R3D.zs$')
	for user, passwd in users:
		conn = omero_tools.connect_to_omero(user, passwd)
		for image in omero_tools.get_images(conn):
			if re.match(pattern, image.getName()):
				print '#' * 50
				print 'from: %s' % image.getName()
				to_name = re.sub(pattern, r'\1R3D_D3D.dv.zs', image.getName())
				image.setName(to_name)
				image.save()
				print 'to  : %s' % image.getName()
		conn._closeSession()

if __name__ == '__main__':
	main()
