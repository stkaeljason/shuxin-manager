# -*- coding:utf-8 -*-
import logging
import logging.config
import os
from flask import Flask, render_template, url_for
from manager.global_var import login_manager, redis_db, cache, dbsession
from manager.models import Admin
from manager.settings import last_settings
from manager.libs import utils
from manager.libs.session import ServerSideSession


def __import_blueprint(blueprint_str):
    split = blueprint_str.split('.')
    module_path = '.'.join(split[0: len(split) - 1])
    variable_name = split[-1]
    mod = __import__(module_path, fromlist=[variable_name])
    return getattr(mod, variable_name)


def app_factory(config=last_settings):
    app = Flask(__name__)
    configure_app(app, config)
    configure_logger(app)
    configure_blueprints(app, config.BLUEPRINTS)
    configure_error_handlers(app)
    configure_database(app)
    configure_redis(app)
    configure_cache(app)
    configure_session(app)
    configure_context_processors(app)
    configure_template_filters(app)
    configure_extensions(app)
    login_manager.init_app(app)
    # configure_sentry(app)
    configure_remove_dbsession(app)

    return app


def configure_app(app, config):
    """Loads configuration class into flask app"""
    app.config.from_object(config)


def configure_logger(app):
    # 配置自定义的logger
    logging.config.fileConfig('conf/log.conf')
    # 配置app的logger
    if not app.debug:
        file_handler = logging.handlers.WatchedFileHandler(
            app.config.get('LOG_FILENAME', 'error.log'), 'a')
        file_formatter = logging.Formatter(app.config.get(
            'LOG_FILE_FORMAT',
            '%(asctime)s %(name)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(app.config.get('LOG_FILE_LEVEL', logging.ERROR))
        app.logger.addHandler(file_handler)
    app.logger.info('Logger started')


def configure_blueprints(app, blueprints):
    """Registers all blueprints set up in config.py"""
    for blueprint_config in blueprints:
        blueprint, kw = None, {}

        if (isinstance(blueprint_config, basestring)):
            blueprint = blueprint_config
        elif (isinstance(blueprint_config, tuple)):
            blueprint = blueprint_config[0]
            kw = blueprint_config[1]
        else:
            print "Error in BLUEPRINTS setup in config.py"
            print '''Please, verify if each blueprint setup is either a
                    string or a tuple.'''
            exit(1)

        blueprint = __import_blueprint(blueprint)
        app.register_blueprint(blueprint, **kw)


def configure_error_handlers(app):
    @app.errorhandler(403)
    def forbidden_page(error):
        """
        The server understood the request, but is refusing to fulfill it.
        Authorization will not help and the request SHOULD NOT be repeated.
        If the request method was not HEAD and the server wishes to make public
        why the request has not been fulfilled, it SHOULD describe the reason
        for the refusal in the entity. If the server does not wish to make this
        information available to the client, the status code 404 (Not Found)
        can be used instead.
        """
        return render_template("error/access_forbidden.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        """
        The server has not found anything matching the Request-URI. No
        indication is given of whether the condition is temporary or permanent.
        The 410 (Gone) status code SHOULD be used if the server knows, through
        some internally configurable mechanism, that an old resource is
        permanently unavailable and has no forwarding address. This status code
        is commonly used when the server does not wish to reveal exactly why
        the request has been refused, or when no other response is applicable.
        """
        return render_template("error/page_not_found.html"), 404

    @app.errorhandler(405)
    def method_not_allowed_page(error):
        """
        The method specified in the Request-Line is not allowed for the
        resource identified by the Request-URI. The response MUST include an
        Allow header containing a list of valid methods for the requested
        resource.
        """
        return render_template("error/method_not_allowed.html"), 405

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("error/server_error.html"), 500

    @app.errorhandler(410)
    def page_gone(error):
        return render_template("error/page_gone.html"), 410


def configure_database(app):
    """Database configuration should be set here"""
    # uncomment for sqlalchemy support
    from manager.database import db

    db.app = app
    db.init_app(app)


def configure_redis(app):
    redis_db.init_app(app)


def configure_cache(app):
    cache.init_app(app)


def configure_session(app):
    ServerSideSession(app)


def configure_context_processors(app):
    """Modify templates context here"""

    @app.context_processor
    def override_url_for():
        def min_url_for(endpoint, **values):
            if endpoint == 'static':
                filename = values.get('filename', None)
                if filename and 'common' in filename and not app.debug:
                    root, ext = os.path.splitext(filename)
                    if ext and ext in ['.js', '.css'] and '.min' not in root:
                        new_ext = ".min" + ext
                        values['filename'] = root + new_ext
                # 调试模式下为每个请求添加一个参数避免缓存影响js调试
                elif filename and app.debug:
                    values['cached'] = utils.now()
            return url_for(endpoint, **values)

        return dict(url_for=min_url_for)


def configure_template_filters(app):
    """Configure filters and tags for jinja"""

    def get_username(email):
        if email:
            u = Admin.query.filter(Admin.email == email).first()
            return u.email if u else "not login"
        return "not login"

    app.jinja_env.filters['get_username'] = get_username


def configure_remove_dbsession(app):
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        try:
            dbsession.remove()
        except:
            pass


def configure_extensions(app):
    """Configure extensions like mail and login here"""
    pass
