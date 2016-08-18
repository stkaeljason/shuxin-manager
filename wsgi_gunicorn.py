#!/usr/bin/env python
# -*- coding: utf-8 -*-
from manager.main import app_factory

app = app_factory()


if __name__ == "__main__":
    app.run(host='10.168.29.182', port=8888)
