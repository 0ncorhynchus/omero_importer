# -*- coding: utf-8 -*-
import os
import re
from functions import *

is_shifted = lambda path: isNotNone(re.match(r'^.*\.zs$', path))
is_deconvoluted = lambda path: isNotNone(re.match(r'^.*\.dv_decon.*$|^.*_D4D\.dv.*$', path))

class ImageFile:

    def __init__(self, path):
        self._path = path
        self._basename = None
        self._origin_name = None
        self._shifted = None
        self._deconvoluted = None

    @property
    def basename(self):
        if self._basename is None:
            self._basename = os.path.basename(self._path)
        return self._basename

    @property
    def is_shifted(self):
        if self._shifted is None:
            self._shifted = (re.match(r'^.*\.zs$', self.basename) is not None)
        return self._shifted

    @property
    def is_deconvoluted(self):
        if self._deconvoluted is None:
            self._deconvoluted = (re.match(r'^.*\.dv_decon.*$|^.*_D3D\.dv.*$',
                self.basename) is not None)
        return self._deconvoluted

    @property
    def origin_name(self):
        if self._origin_name is None:
            tmp = self.basename
            if (self.is_shifted):
                tmp = tmp[:-3]
            tmp = re.sub(r'^(.*)\.dv_decon$', r'\1.dv', tmp)
            tmp = re.sub(r'^(.*)_D3D\.dv$', r'\1.dv', tmp)
            self._origin_name = tmp
        return self._origin_name
