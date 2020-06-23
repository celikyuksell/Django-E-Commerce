# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six


def unpack_styles(styles):
    ''' combine a dictionary of CSS property/value pairs into a string '''
    return '; '.join([': '.join(i) for i in six.iteritems(styles)])
