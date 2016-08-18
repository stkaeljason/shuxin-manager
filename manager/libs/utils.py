#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import os
import sys
import time
from flask import request
from flask.json import JSONEncoder
from PIL import Image
import uuid
reload(sys)
sys.setdefaultencoding('utf-8')


def get_uuid():
    return uuid.uuid4().hex


def now():
    return int(round(time.time() * 1000))


def millisecond_to_datestr(millisecond):
    s = datetime.fromtimestamp(millisecond / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return s


def get_image_upload_name(filepath, prefix=None):
    img = Image.open(filepath)
    wxh = '%dx%d' % img.size
    img.close()

    t = datetime.now().strftime("%Y%m%d%H%M%S%f")

    if prefix:
        s = '{prefix}/{wxh}/{t}'.format(prefix=prefix, wxh=wxh, t=t)
    else:
        s = '{wxh}/{t}'.format(prefix=prefix, wxh=wxh, t=t)

    ext = os.path.splitext(filepath)[-1]
    if ext:
        s += ext

    return s


def reduce_image_size(imgpath, optimize=True, quality=25):
    if not os.path.exists(imgpath):
        return

    im = Image.open(imgpath)
    im.save(imgpath, optimize=optimize, quality=quality)
    im.close()


class CustomJsonEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return int(time.mktime(obj.timetuple())) * 1000 + obj.microsecond / 1000
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


def get_int_arg(arg, default, location='args'):
    assert location in ['args', 'json', 'form']
    if location == 'args':
        value = request.args.get(arg, default)
    elif location == 'json':
        value = request.json.get(arg, default)
    elif location == 'form':
        value = request.form.get(arg, default)
    try:
        value = int(value)
    except:
        return default
    return value


def get_arg(arg_name, default, valid_values=[], location="args"):
    assert location in ['args', 'json']
    if location == 'args':
        arg = request.args.get(arg_name, default)
    elif location == 'json':
        arg = request.json.get(arg_name, default)
    if valid_values:
        if arg not in valid_values:
            return default
    return arg


def get_datetime_arg(arg, location='args'):
    if location == 'args':
        value = request.args.get(arg, "")
    elif location == 'form':
        value = request.form.get(arg, "")
    else:
        value = ""
    if value:
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except:
            return ""
    return value


def check_image_size(filename, max_size):
    if os.path.isfile(filename):
        filesize = os.path.getsize(filename)
        if filesize <= max_size:
            return True
    return False


def add_pagination_args(pagination, res):
    res['page'] = pagination.page
    res['per_page'] = pagination.per_page
    res['pages'] = pagination.pages
    res['total'] = pagination.total
