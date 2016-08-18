#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import timedelta
import logging

# misc
PROJECT_NAME = 'shuxin_manager'
USE_X_SENDFILE = False
CSRF_ENABLED = True
SECRET_KEY = "92aad4950fcc9144b1e2fe6be6eb3541e36940a6278c13a7"

# sqlalchemy
SQLALCHEMY_POOL_SIZE = 5
SQLALCHEMY_MAX_OVERFLOW = 20
SQLALCHEMY_POOL_RECYCLE = 1200
SQLALCHEMY_POOL_TIMEOUT = 100

# LOGGING
LOG_FILENAME = "error.log"
LOG_FILE_LEVEL = logging.DEBUG
LOG_FILE_FORMAT = "%(asctime)s %(name)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"

# see example/ for reference
# ex: BLUEPRINTS = ['blog.app']  # where app is a Blueprint instance
# where app is a Blueprint instance
# ex: BLUEPRINTS = [('blog.app', {'url_prefix': '/myblog'})]
BLUEPRINTS = [
    ('manager.views.admin.app', {'url_prefix': '/shuxin-manager'}),
]

# used by login_manager
SESSION_PROTECTION = None

# cookie
REMEMBER_COOKIE_DURATION = timedelta(days=7)

# session
PERMANENT_SESSION_LIFETIME = timedelta(days=7)
SESSION_COOKIE_NAME = PROJECT_NAME
SESSION_KEY_PREFIX = PROJECT_NAME
SESSION_SALT = 'VmtaYVUyTnJOVlpPVmxaaFRVaE9URU5uUFQwSwo'

# 返回码
FAILED = -1
SUCCESS = 0

# redis cache
CACHE_DEFAULT_TIMEOUT = 5 * 60
CACHE_TYPE = 'redis'
CACHE_KEY_PREFIX = "cache:"

# upload folder
UPLOAD_FOLDER = '/tmp/upload'
