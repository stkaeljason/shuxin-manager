#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask.ext.login import UserMixin
from werkzeug import generate_password_hash, check_password_hash
from manager.database import db


class BaseModel(object):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    @property
    def columns(self):
        return [c.name for c in self.__table__.columns]

    def parse_items_with_type(self, d, type):
        pass

    def __repr__(self):
        return "<%s('%d')>" % (self.__class__.__name__, self.id)


class Admin(db.Model, BaseModel, UserMixin):
    __tablename__ = 'admin'

    email = db.Column(db.String(36), unique=True)
    password = db.Column(db.String(2048))
    active = db.Column(db.Boolean, default=False)

    def __init__(self, email, password, active=False):
        self.email = email
        self.password = generate_password_hash(password)
        self.active = active

    def __repr__(self):
        return "<Admin('%d', '%s', '%s')>" \
               % (self.id, self.username, self.email)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        if check_password_hash(self.password, password):
            self.active = True
            return True

        return False
