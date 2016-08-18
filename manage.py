#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask.ext.script import Manager, Server
from manager import commands
from manager.main import app_factory


if __name__ == "__main__":
    server = Server(host="0.0.0.0", port=8887)
    manager = Manager(app_factory)
    manager.add_command("runserver", server)
    manager.add_command("drop_db", commands.DropDB())
    manager.add_command("create_db", commands.CreateDB())
    manager.add_command("create_admin", commands.CreateAdmin())
    manager.run()
