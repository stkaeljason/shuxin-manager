# -*- coding:utf-8 -*-
from flask.ext.script import Command, Option
from manager.database import db


class CreateAdmin(Command):
    option_list = (
        Option('--loginname', dest='loginname', required=True),
        Option('--password', dest='password', required=True),
    )

    def run(self, loginname, password):
        from manager import models_handle
        from manager.models import Admin

        user = Admin(loginname, password)
        db.session.add(user)
        models_handle.dbcommit()


class CreateDB(Command):
    """Creates sqlalchemy database"""

    def run(self):
        from manager.database import create_all

        create_all()


class DropDB(Command):
    """Drops sqlalchemy database"""

    def run(self):
        from manager.database import drop_all

        drop_all()
