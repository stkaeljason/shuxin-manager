# -*- coding: utf-8 -*-
from uuid import uuid4
import hashlib
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin
from itsdangerous import BadSignature, URLSafeTimedSerializer
from flask import json
from manager.global_var import redis_session


class JSONSerializer():
    def dumps(self, value):
        return json.dumps(value)

    def loads(self, value):
        return json.loads(value)


session_json_serializer = JSONSerializer()


class RedisSession(CallbackDict, SessionMixin):
    """Baseclass for server-side based sessions."""

    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.modified = False

    def __repr__(self):
        return "<RedisSession {'sid': %s}>" % self.sid


class RedisSessionInterface(SessionInterface):
    serializer = session_json_serializer
    session_class = RedisSession
    key_derivation = 'hmac'
    digest_method = staticmethod(hashlib.sha1)
    redis = redis_session

    def __init__(self, app):
        self.key_prefix = app.config.get('SESSION_KEY_PREFIX', 'session:')
        self.salt = app.config.get('SESSION_SALT', 'salt')

    def _generate_sid(self):
        return str(uuid4())

    def open_session(self, app, request):
        s = self.get_signing_serializer(app)
        if s is None:
            return None
        val = request.cookies.get(app.session_cookie_name)
        if not val:
            return self.session_class(sid=self._generate_sid())
        try:
            data = s.loads(val)
            sid = data.get('sid', None)
            user_id = data.get('user_id', None)
            if sid and isinstance(sid, basestring):
                val = self.redis.get(self.key_prefix + sid)
                if val is not None:
                    try:
                        data = self.serializer.loads(val)
                        if data.get('user_id', None) != user_id:
                            return self.session_class(sid=self._generate_sid())
                        return self.session_class(data, sid=sid)
                    except:
                        pass
            return self.session_class(sid=self._generate_sid())
        except (BadSignature, Exception):
            return self.session_class(sid=self._generate_sid())

    def get_signing_serializer(self, app):
        if not app.secret_key:
            return None
        signer_kwargs = dict(
            key_derivation=self.key_derivation,
            digest_method=self.digest_method,
        )
        return URLSafeTimedSerializer(app.secret_key, salt=self.salt,
                                      serializer=self.serializer,
                                      signer_kwargs=signer_kwargs)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            if session.modified:
                self.redis.delete(self.key_prefix + session.sid)
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain, path=path)
            return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.setex(self.key_prefix + session.sid,
                         int(app.permanent_session_lifetime.total_seconds()),
                         val)
        cookie_val = self.get_signing_serializer(app).dumps(
            dict({'sid': session.sid, 'user_id': session.get('user_id', None)}))
        response.set_cookie(app.session_cookie_name, cookie_val,
                            expires=expires, httponly=httponly,
                            domain=domain, path=path, secure=secure)


class ServerSideSession():
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.session_interface = RedisSessionInterface(app)
