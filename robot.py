#! -*- coding: utf-8 -*-

import sys
import json
import re
from omero_import import omero_tools
from omero_import.imagefile import ImageFile
from settings import USERS

def search_duplicated_images():
    print '[search_duplicated_images]'
    tmp = {}
    zszs = []
    for user in USERS:
        print '+ %s' % user
        conn = omero_tools.connect_to_omero(
                user, USERS[user]['PASSWORD'])
        images = omero_tools.get_images(conn)
        for image in images:
            name = image.getName()
            img_id = image.getId()
            obj = {
                    'user' : user,
                    'dataset' : image.getDataset().getName(),
                    'name' : name,
                    'id' : img_id
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

def clean_cstwice():
    print '[search_images_chromatic_shifted_twice]'
    for user in USERS:
        print '+ %s' % user
        zszs = []
        conn = omero_tools.connect_to_omero(
                user, USERS[user]['PASSWORD'])
        images = omero_tools.get_images(conn)
        for image in images:
            name = image.getName()
            img_id = image.getId()
            if re.match(r'^.*\.zs\.zs$', name) is not None:
                zszs.append(img_id)
                continue

        omero_tools.delete_objects(conn, 'Image', zszs,
                True, True)
        conn._closeSession()

def main():
    argv = sys.argv
    argc = len(argv)
    if argc == 2:
        if argv[1] == 'check':
            search_duplicated_images()
    elif  argc == 3:
        if argv[1] == 'clean':
            if argv[2] == 'cstwice':
                clean_cstwice()

if __name__ == '__main__':
    main()
