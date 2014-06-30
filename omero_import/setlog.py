# -*- coding: utf-8 -*-
# written by S.Kato
# USAGE: python setlog.py <LOG FILE> <IMAGE FILE> [OPTION TITLE]

import os
import sys
import re
import struct

    #header_format = '<iiiiiiiiiiffffffiiifffiihhi24shhhhffffffhhhhhhffhhfffhhhhhhfffi'
    #title_format = '80s80s80s80s80s80s80s80s80s80s'

log_formats = [
        {'title': 'image_file', 'regular': r'(\s*)Resolve3D Image File:(\s*)'},
        {'title': 'created', 'regular': r'(\s*)Created(\s*)'},
        {'title': 'objective', 'regular': r'(\s*)Objective:(\s*)'},
        {'title': 'type', 'regular': r'(\s*)Type:(\s*)'},
        {'title': 'gain', 'regular': r'(\s*)Gain:(\s*)'},
        {'title': 'speed', 'regular': r'(\s*)Speed:(\s*)'},
        {'title': 'sectionz', 'regular': r'(\s*)SECTIONZ(\s*)'},
        {'title': 'coordinates', 'regular': r'(\s*)Stage coordinates:(\s)'}]

regulars = [
        r'(\s*)Resolve3D Image File:(\s*)',
        r'(\s*)Created(\s*)',
        r'(\s*)Objective:(\s*)',
        r'(\s*)Type:(\s*)',
        r'(\s*)Gain:(\s*)',
        r'(\s*)Speed:(\s*)',
        r'(\s*)SECTIONZ(\s*)',
        r'(\s*)Stage coordinates:(\s)']
titles = [
        'image_file',
        'created',
        'objective',
        'type',
        'gain',
        'speed',
        'sectionz',
        'coordinates']
filters = [
        r'(\s*)FILTERS(\s*)',
        r'(\s*)CCD(\s*)']

def translate_space(string):
    return string.lstrip().rstrip('\n').rstrip()
#    string = string.lstrip()
#    string = string.rstrip('\n')
#    string = string.rstrip()
#    return string

def translate_80s(string):
    length = len(string)
    for i in range(80-length):
        string = string+' '
    return string

def read_log_file(logfile_name):
    data = {}
    data.update({'filters':[]})
    for title in titles:
        data[title] = ''
    logfile = open(logfile_name,'r')
    lines = logfile.readlines()
    logfile.close()
    for n in range(len(lines)):
        line = lines[n]
        for i in range(len(regulars)):
            match = re.match(regulars[i],line)
            if match:
                data.update({titles[i]:translate_space(line[match.end():])})
                break

        filter_match = re.match(filters[0],line)
        if filter_match:
            ccd_line = lines[n+2]
            ccd_match = re.match(filters[1],ccd_line)
            if ccd_match:
                f = translate_space(line[filter_match.end():])
                c = translate_space(ccd_line[ccd_match.end():])
                data['filters'].append({'filter':f,'ccd':c})
                n = n+2

    return data

def write_log(logfile_name,imagefile_name,option_title=''):
    if not os.path.exists(logfile_name):
        #print 'LOG FILE : %s does not exist.'%logfile_name
        return False
    if not os.path.exists(imagefile_name):
        #print 'IMAGE FILE : %s does not exist.'%imagefile_name
        return False

    #print 'LOG FILE: %s'%logfile_name
    #print 'IMAGE FILE: %s'%imagefile_name

    log = read_log_file(logfile_name)

    imagefile = open(imagefile_name,'r+b')

    imagefile.seek(208)
    coordinate = log['coordinates']
    s = coordinate.index('(')
    d = coordinate.index(',')
    x = coordinate[s+1:d]
    coordinate = coordinate[d+1:]
    s = 0
    d = coordinate.index(',')
    y = coordinate[s:d]
    coordinate = coordinate[d+1:]
    d = coordinate.index(')')
    z = coordinate[s:d]

    x = float(x)
    y = float(y)
    z = float(z)

    imagefile.write(struct.pack('fff',z,x,y))

    imagefile.seek(224)

    imagefile.write(translate_80s(log['image_file']))
    imagefile.write(translate_80s(log['created']))
    imagefile.write(translate_80s(log['objective']))
    imagefile.write(translate_80s('%s %s %s' % (log['type'],log['gain'],log['speed'])))
    f = log['filters']
    for i in range(len(f)):
        imagefile.write(translate_80s('%s %s' % (f[i]['filter'],f[i]['ccd'])))
    imagefile.write(translate_80s('SECTIONZ %s' % log['sectionz']))
    imagefile.write(translate_80s(option_title))
    imagefile.close()

    return True

if __name__ == '__main__':
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print 'USAGE: python setlog.py <LOG FILE> <IMAGE FILE> [OPTION TITLE]'
        sys.exit()

    logfile_name = sys.argv[1]
    imagefile_name = sys.argv[2]
    if len(sys.argv) == 4:
        option_title = sys.argv[3]
    else:
        option_title = ''

    write_log(logfile_name,imagefile_name,option_title)

