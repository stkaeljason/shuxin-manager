# -*- coding:utf-8 -*-
import os
from flask import Blueprint, render_template, request, url_for, \
    redirect, session, flash, current_app
from flask.ext.login import login_required, login_user, logout_user
from sqlalchemy.orm import exc as orm_exc
from manager.models import Admin
from manager.global_var import login_manager
from manager.libs.qiniuwrapper import QiniuWrapper
from manager.libs.utils import get_image_upload_name, reduce_image_size
from manager import models_handle
import json
from manager.global_var import redis_db
from werkzeug.utils import secure_filename
from manager.settings.last_settings import UPLOAD_FOLDER
import sys

reload(sys)
sys.setdefaultencoding('utf8')

app = Blueprint('admin', __name__)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('.signin'))


@login_manager.user_loader
def load_user(userid):
    return Admin.query.filter_by(id=userid).first()


@app.route('/signin/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST' and request.form:
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        try:
            user = Admin.query.filter_by(email=email).one()
        except orm_exc.NoResultFound:
            flash("用户名不存在")
            return render_template('access/AdminLogin.html')
        if not user.check_password(password):
            flash("密码错误")
            return render_template('access/AdminLogin.html')
        login_user(user)
        # save user email in session for java cms use to display user info
        session['email'] = user.email
        return redirect(url_for('.get_user'))
    else:
        return render_template('access/AdminLogin.html')


@app.route('/signout/')
@login_required
def signout():
    logout_user()
    session.pop('user_email', None)
    return redirect(url_for('.signin'))


@app.route('/')
@login_required
def index():
    return redirect(url_for('.signin'))


@app.route('/user')
@login_required
def get_user():
    return render_template('user/user.html')


@app.route('/get_user', methods=['POST'])
@login_required
def get_user_list():
    start = request.values.get('start')
    limit = request.values.get('limit')
    start = int(start)
    limit = int(limit)
    print start
    print limit
    res = models_handle.get_users(start, limit)
    return json.dumps(res)


@app.route('/post', methods=['POST', 'GET'])
@login_required
def get_postinfo():
    start = request.values.get('start')
    limit = request.values.get('limit')
    start = int(start)
    limit = int(limit)
    res = models_handle.get_post(start, limit)
    current_app.logger.debug(res)
    return json.dumps(res)


@app.route('/post/send', methods=['GET', 'POST'])
@login_required
def send_post():
    if request.method == 'GET':
        users = models_handle.get_admin_users()
        groups = models_handle.get_groups()
        return render_template('user/send_post.html', users=users, groups=groups)
    elif request.method == 'POST':
        # 获取form表单
        uid = request.form.get('uid', None)
        realname = ''
        if uid and '/' in uid:
            realname = uid.split('/')[0].strip()
            uid = uid.split('/')[1].strip()
        nickname = request.form.get('nickname', None)
        group_name = request.form.get('group_name', None)
        if group_name:
            group_name, group_id, group_class = [s.strip() for s in group_name.split('/')]
        content = request.form.get('content', None)
        imgs = []

        for filestorage in request.files.getlist("picture[]"):
            # Workaround: larger uploads cause a dummy file named '<fdopen>'.
            # See the Flask mailing list for more information.
            if filestorage.filename and filestorage.filename not in (None, 'fdopen', '<fdopen>'):
                if (not os.path.exists(UPLOAD_FOLDER)):
                    os.makedirs(UPLOAD_FOLDER)
                filename = secure_filename(filestorage.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                filestorage.save(filepath)
                reduce_image_size(filepath)

                qiniu = QiniuWrapper()
                key = get_image_upload_name(filepath, prefix='post')
                success, info = qiniu.upload_file(key, filepath)
                if success:
                    imgs.append(key)
                else:
                    current_app.logger.error('upload <%s> failed' % filepath)

        avatar = request.files['avatar']
        if avatar:
            avatarname = secure_filename(avatar.filename)
            avatarpath = os.path.join(UPLOAD_FOLDER, avatarname)
            avatar.save(avatarpath)
            reduce_image_size(avatarpath)
            qiniu = QiniuWrapper()
            key = get_image_upload_name(avatarpath, prefix='user')
            success, info = qiniu.upload_file(key, avatarpath)
            if success:
                avatar = key
                current_app.logger.debug('upload avatar <%s> success' % key)
            else:
                current_app.logger.error('upload avatar <%s> failed' % avatarpath)

        else:
            avatar = models_handle.getuserinfo_byname(realname)['avatar']
            current_app.logger.debug('using user default avatar: %s' % avatar)

        res = models_handle.add_post(
            author_id=uid,
            nickname=nickname,
            parent_id=group_id,
            group_name=group_name,
            content=content,
            pictures=imgs,
            avatar=avatar)

    current_app.logger.debug(res)
    return redirect(url_for('.comment'))


@app.route('/push', methods=['GET'])
@login_required
def push():
    return render_template('user/push.html')


@app.route('/sendpush', methods=['POST'])
def sendpush():
    groupName = request.form['group_name'].split('/')[0].strip()
    groupId = request.form['group_name'].split('/')[1].strip()
    pushContent = request.form['content']
    print groupName
    print groupId
    print pushContent
    # return redirect(url_for('.push'))
    return render_template('user/push.html', info="发送成功")


@app.route('/comment')
@login_required
def comment():
    return render_template('user/comment.html')


@app.route('/get_post_count', methods=['POST'])
@login_required
def post_count():
    res = models_handle.get_post_count()

    count = 0
    for i in res:
        count = i.values()[0]
    return str(count)


@app.route('/get_user_count', methods=['POST'])
@login_required
def user_count():
    res = models_handle.get_user_count()
    count = 0
    for i in res:
        count = i.values()[0]
    print count
    return str(count)


@app.route('/get_comment', methods=['POST'])
@login_required
def get_comment():
    root_id = request.values.get('id')
    res = models_handle.get_comment(root_id)
    current_app.logger.debug(res)
    return json.dumps(res)


@app.route('/post_comment', methods=['POST'])
@login_required
def post_comment():
    return 'ok'


@app.route('/getuid_byname', methods=['GET', 'POST'])
@login_required
def get_uid():
    uid = ''
    if request.method == 'GET':
        uid = models_handle.getuid_byname(request.args.get('nickname'))
    else:
        uid = models_handle.getuid_byname(request.form.get('nickname'))
    return str(uid)


@app.route('/get_groups_by_rule', methods=['GET'])
@login_required
def get_groups_by_rule():
    rule = request.args.get('rule')
    groups = models_handle.get_groups_by_rule(rule)
    current_app.logger.debug(groups)
    return json.dumps(groups)


@app.route('/group')
@login_required
def get_group():
    res = models_handle.get_groups_by_rule('')
    # current_app.logger.debug(res)
    return render_template('user/group.html', res=res)


@app.route('/get_allGroup')
@login_required
def get_groups():
    res = models_handle.get_groups_by_rule(None)
    return json.dumps(res)


@app.route('/topic')
@login_required
def topic():
    return render_template('user/topic.html')


@app.route('/topic/new_topic', methods=['GET', 'POST'])
@login_required
def new_topic():
    if request.method == 'GET':
        users = models_handle.get_admin_users()
        groups = models_handle.get_groups_by_rule('')
        return render_template('user/send_topic.html', users=users, groups=groups)

    if request.method == 'POST':
        background = request.files['background']
        if background:
            if (not os.path.exists(UPLOAD_FOLDER)):
                os.mkdir(UPLOAD_FOLDER)
            backgroundname = secure_filename(background.filename)
            backgroundpath = os.path.join(UPLOAD_FOLDER, backgroundname)
            background.save(backgroundpath)
            reduce_image_size(backgroundpath)
            qiniu = QiniuWrapper()
            key = get_image_upload_name(backgroundpath, prefix='user')
            success, info = qiniu.upload_file(key, backgroundpath)
            if success:
                background = key
                current_app.logger.debug('upload avatar <%s> success' % key)
            else:
                current_app.logger.error('upload avatar <%s> failed' % backgroundpath)

        else:
            background = 'http://image.ciwei.io/group/background/recentdays.jpg'
            current_app.logger.debug('using user default avatar: %s' % background)
        topicName = request.form['topicName']
        if request.form['type'] == 'group':
            # containerId = request.form['group_name'].split('/')[1].strip()
            # containerName = request.form['group_name'].split('/')[0].strip()
            containerId = [s.strip().split('/')[1] for s in request.form.getlist('group_name[]')]
            containerName = [s.strip().split('/')[0] for s in request.form.getlist('group_name[]')]
        else:
            containerId = ['ALL']
            containerName = ['属信']
        res = models_handle.add_topic(
            topicName=topicName,
            containerName=containerName,
            containerId=containerId,
            background=background
        )
        current_app.logger.debug(res)
        return redirect(url_for('.new_topic'))
    else:
        return 'illegal method'
