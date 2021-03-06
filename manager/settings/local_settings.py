#!/usr/bin/env python
# -*- coding: utf-8 -*-
from redis import ConnectionPool


DEBUG = True
SQLALCHEMY_ECHO = True
TESTING = False
JSONIFY_PRETTYPRINT_REGULAR = True
LOGIN_DISABLED = True


# DATABASE CONFIGURATION
DB_USER = 'shuxin'
DB_PASSWD = 'shuxin123'
DB_HOST = 'localhost'
DB_PORT = 3306
DB_NAME = 'shuxin'
CONNECT_DB_NAME = 'connect'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
    DB_USER, DB_PASSWD, DB_HOST, DB_PORT, DB_NAME)

CONNECT_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
    DB_USER, DB_PASSWD, DB_HOST, DB_PORT, CONNECT_DB_NAME)

# dse-service url
DSE_SERVICE_GROUP_URL = 'https://api-test.ciwei.io/dse-service/v1/app/{uid}/group'
DSE_SERVICE_ALL_GROUP_URL = 'https://api-test.ciwei.io/dse-service/v1/admin/groups'
DSE_SERVICE_POST_URL = 'https://api-test.ciwei.io/dse-service/v1/admin/post'

# REDIS SETTINGS
REDIS_HOST = 'localhost'
REDIS_PASSWORD = None
REDIS_DATABASE = 0  # get user token
REDIS_PORT = 6379
REDIS_URL = "redis://%s:%d/%d" % (REDIS_HOST, REDIS_PORT, REDIS_DATABASE)

# redis cache setting
CACHE_REDIS_HOST = 'localhost'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_PASSWORD = None
CACHE_REDIS_DB = 1  # cache
CACHE_CONNECTION_POOL = ConnectionPool(
    host=CACHE_REDIS_HOST,
    port=CACHE_REDIS_PORT,
    password=CACHE_REDIS_PASSWORD,
    db=CACHE_REDIS_DB)
CACHE_OPTIONS = {'connection_pool': CACHE_CONNECTION_POOL}

# user session setting
SESSION_REDIS_HOST = 'localhost'
SESSION_REDIS_PORT = 6379
SESSION_REDIS_PASSWORD = None
SESSION_REDIS_DB = 2  # user session
SESSION_CONNECT_POOL = ConnectionPool(
    host=SESSION_REDIS_HOST,
    port=SESSION_REDIS_PORT,
    password=SESSION_REDIS_PASSWORD,
    db=SESSION_REDIS_DB
)

# qiniu
QINIU_ACCESS_KEY = '64BCBLsNbBJ-RAcX8FktE8fWe4HIkmXNYm1u9RVW'
QINIU_SECRET_KEY = 'eknnx5XshyeJx-I0BvFe9FMfRkfdCExEmPu3N1Q8'
QINIU_BUCKET_NAME = 'connect'
