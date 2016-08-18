#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from common_settings import *
mode = os.environ.get('DEPLOY_MODE', 'production')

print "Load %s settings......" % mode
if mode == 'local':
    from local_settings import *
elif mode == 'production':
    from production_settings import *
else:
    raise ValueError("Invalid deploy mode")
