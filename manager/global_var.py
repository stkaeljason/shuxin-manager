#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.login import LoginManager
from flask.ext.redis import FlaskRedis
from flask.ext.cache import Cache
from redis import StrictRedis
from manager.settings.last_settings import (CONNECT_DATABASE_URI,
    SESSION_CONNECT_POOL)
from manager.database import get_db_session

login_manager = LoginManager()
redis_db = FlaskRedis()
cache = Cache()
dbsession = get_db_session(CONNECT_DATABASE_URI)
redis_session = StrictRedis(connection_pool=SESSION_CONNECT_POOL)
