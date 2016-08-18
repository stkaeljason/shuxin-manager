#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import current_app
from manager.global_var import cache, dbsession, redis_db
from manager.settings.last_settings import (
    DSE_SERVICE_GROUP_URL, DSE_SERVICE_ALL_GROUP_URL, DSE_SERVICE_POST_URL,
    DSE_SERVICE_TOPIC_URL, CONNECT_DATABASE_URI, GROUPS_RULE
)
from manager.libs.utils import millisecond_to_datestr, now
from manager.database import get_db_session
import requests
import hashlib

DBSESSION = dbsession


def check_dbsession(dbsession):
    try:
        dbsession.execute('select 1')
    except:
        global DBSESSION
        DBSESSION = get_db_session(CONNECT_DATABASE_URI)


@cache.memoize(timeout=30)
def get_user(start, limit):
    global DBSESSION
    check_dbsession(DBSESSION)
    limit = limit - start
    sql = 'SELECT uid, nickname, update_time FROM profile ORDER BY update_time DESC limit ' + str(start) + ',' + str(
        limit)
    users = DBSESSION.execute(sql)
    res = []
    for u in users:
        res.append({
            'uid': u.uid,
            'nickname': u.nickname,
            'update_time': millisecond_to_datestr(u.update_time),
        })

    return res


def get_users(start, limit):
    global DBSESSION
    check_dbsession(DBSESSION)
    limit = limit - start
    res = []
    sql = 'SELECT uid, nickname, update_time FROM profile ORDER BY update_time DESC limit ' + str(start) + ',' + str(
        limit)
    users = DBSESSION.execute(sql)
    print users
    for u in users:
        uid = u.uid
        nickname = u.nickname
        update_time = u.update_time
        # access redis get user token
        token = redis_db.get("USER:ACCESS-TOKEN:" + str(uid))
        # 目前正式环境还没有启用前缀，估获取了两次
        token = token if token else redis_db.get(str(uid))
        if not token:
            current_app.logger.error('can not get token for uid: %s' % uid)
            continue
        # access dse-service API get user groups by uid: /v1/app/{uid}/group
        url = DSE_SERVICE_GROUP_URL.format(uid=uid)
        headers = {
            'content-type': 'application/json',
            'X-ACCESS-TOKEN': token,
        }
        req = requests.get(url, headers=headers)

        if req.status_code != 200:
            err_msg = 'get <%s, %s> groups error: %s' % (uid, nickname, req.content)
            groups = err_msg
            current_app.logger.error(err_msg)
        else:
            groups = ', '.join([x['gname'] for x in req.json()['data']])

        res.append({
            'uid': uid,
            'nickname': nickname,
            'update_time': update_time,
            'groups': groups,
        })

    return res


def get_post(start, limit):
    global DBSESSION
    check_dbsession(DBSESSION)
    limit = limit - start
    sql = 'SELECT * FROM post WHERE status=0 ORDER BY update_time DESC limit ' + str(start) + ',' + str(limit)
    posts = DBSESSION.execute(sql)
    res = []
    for p in posts:
        res.append({
            'id': p.id,
            'parent_id': p.parent_id,
            'author_id': p.author_id,
            'nickname': p.nickname,
            'avatar': 'http://image.ciwei.io/' + p.avatar,
            'group_name': p.group_name,
            'content': p.content,
            'pictures': p.pictures,
            'comment_count': p.comment_count,
            'like_count': p.like_count,
            'update_time': millisecond_to_datestr(p.update_time),
        })

    return res


def get_post_count():
    global DBSESSION
    check_dbsession(DBSESSION)
    sql = 'SELECT count(*) FROM post WHERE status=0;'
    return DBSESSION.execute(sql)


def get_user_count():
    global DBSESSION
    check_dbsession(DBSESSION)
    sql = 'SELECT count(*) FROM profile'
    return DBSESSION.execute(sql)


def get_comment(root_id):
    global DBSESSION
    check_dbsession(DBSESSION)
    sql = 'SELECT * FROM comment WHERE status=0 AND root_id="' + root_id + '" ORDER BY update_time DESC'
    comments = DBSESSION.execute(sql)
    res = []

    for c in comments:
        res.append({
            'id': c.id,
            'parent_id': c.parent_id,
            'reply_user': c.reply_user,
            'root_id': c.root_id,
            'content': c.content,
            'author_id': c.author_id,
            'nickname': c.nickname,
            'avatar': 'http://image.ciwei.io/' + c.avatar,
            'type': c.type,
            'comment_count': c.comment_count,
            'like_count': c.like_count,
            'update_time': millisecond_to_datestr(c.update_time)
        })
    return res


def add_post(author_id, nickname, avatar, parent_id, group_name, content, pictures):
    magic_number = "???CIWEI-CO[.]"
    timestamp = str(now())
    token = hashlib.md5(timestamp + magic_number).hexdigest()
    url = DSE_SERVICE_POST_URL
    headers = {
        'content-type': 'application/json',
    }
    data = {
        "privateToken": token,
        "timestamp": timestamp,
        "content": {
            "parentId": parent_id,
            "groupName": group_name,
            "content": content,
            "pictures": pictures,
            "authorId": author_id,
            "nickname": nickname,
            "avatar": avatar,
            "type": 0,
        },
    }

    current_app.logger.debug('add_post data:')
    current_app.logger.debug(data)
    req = requests.post(url, headers=headers, json=data)
    current_app.logger.debug(req.content)
    return req.json()


def add_topic(topicName, background, containerId, containerName):
    magic_number = "???CIWEI-CO[.]"
    timestamp = str(now())
    token = hashlib.md5(timestamp + magic_number).hexdigest()
    url = DSE_SERVICE_TOPIC_URL
    headers = {
        'content-type': 'application/json',
    }
    data = {
        "privateToken": token,
        "timestamp": timestamp,
        "data": {
            "topicName": topicName,
            "background": background,
            "containerId": containerId,
            "containerName": containerName
        }
    }
    current_app.logger.debug('add_topic data:')
    current_app.logger.debug(data)
    req = requests.post(url, headers=headers, json=data)
    return req.json()


"""
def get_users():
    global DBSESSION
    check_dbsession(DBSESSION)
    res = []
    sql = 'SELECT uid, nickname FROM profile'
    users = DBSESSION.execute(sql)
    for u in users:
        res.append({
            'uid': u.uid,
            'nickname': u.nickname,
        })

    return res
"""


def get_admin_users():
    global DBSESSION
    check_dbsession(DBSESSION)
    res = []
    sql = 'SELECT uid,nickname FROM profile WHERE nickname IN ("私人管家","张宇")'
    users = DBSESSION.execute(sql)
    for u in users:
        res.append({
            'nickname': u.nickname,
            'uid': u.uid
        })
    return res


def get_groups():
    global DBSESSION
    check_dbsession(DBSESSION)
    res = []
    sql = 'select distinct(parent_id), group_name from post'
    groups = DBSESSION.execute(sql)
    for g in groups:
        res.append({
            'group_id': g.parent_id,
            'group_name': g.group_name,
        })

    return res


def get_groups_by_rule(group_rule):
    magic_number = "???CIWEI-CO[.]"
    timestamp = str(now())
    url = DSE_SERVICE_ALL_GROUP_URL
    headers = {
        'content-type': 'application/json',
    }
    if group_rule is not '':
        token = hashlib.md5(timestamp + magic_number + group_rule).hexdigest()
        data = {
            "privateToken": token,
            "timestamp": timestamp,
            "rule": group_rule,
        }
        req = requests.get(url, headers=headers, json=data, verify=True)
        res = req.json()
    else:
        res = []
        # for r in GROUPS_RULE:
        token = hashlib.md5(timestamp + magic_number + '').hexdigest()
        data = {
            "privateToken": token,
            "timestamp": timestamp,
            "rule": '',
        }
        req = requests.get(url, headers=headers, json=data, verify=True)
        res.append(req.json())
    return res


def getuserinfo_byname(name):
    global DBSESSION
    check_dbsession(DBSESSION)
    sql = 'SELECT uid,avatar from profile WHERE nickname="' + name + '"'
    res = {}
    r = DBSESSION.execute(sql)
    for u in r:
        res['avatar'] = u.avatar
        res['uid'] = u.uid
    return res
