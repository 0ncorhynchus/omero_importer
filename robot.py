#! -*- coding: utf-8 -*-

import json
import re
import omero_tools
from imagefile import ImageFile
from data import users

def search_duplicated_images():
    print '[search_duplicated_images]'
    tmp = {}
    zszs = []
    for user in users:
        print '+ %s' % user
        conn = omero_tools.connect_to_omero(
                user, users[user]['passwd'])
        images = omero_tools.get_images(conn)
        for image in images:
            name = image.getName()
            obj = {
                    'user' : user,
                    'dataset' : image.getDataset().getName(),
                    'name' : name
                    }
            print '|- %s in %s' % (name, image.getDataset().getName())
            if re.match(r'^.*\.zs\.zs$', name) is not None:
                zszs.append(obj)
                continue

            file_obj = ImageFile(name)
            if file_obj.origin_name in tmp:
                tmp[file_obj.origin_name].append(obj)
            else:
                tmp[file_obj.origin_name] = [obj,]

        print ''
        conn._closeSession()

    replicated = []
    for origin in tmp:
        if len(tmp[origin]) > 1:
            replicated.append(tmp[origin])

    replicated_out = open('replicated.json', 'w')
    print >> replicated_out, json.dumps(replicated, sort_keys=True, indent=4)
    replicated_out.close()

    zszs_out = open('chromatic_shifted_twice.json', 'w')
    print >> zszs_out, json.dumps(zszs, sort_keys=True, indent=4)
    zszs_out.close()

def main():
    search_duplicated_images()

if __name__ == '__main__':
    main()
