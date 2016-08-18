# -*- coding:utf-8 -*-


# uncomment for sqlalchemy support
from flask.ext.sqlalchemy import Pagination, orm, SQLAlchemy
import flask.ext.sqlalchemy as sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool
from manager.settings.last_settings import (SQLALCHEMY_POOL_SIZE,
    SQLALCHEMY_POOL_RECYCLE)


def custom_paginate(cls, page, per_page=20, error_out=False):
    """Returns `per_page` items from page `page`.  By default it will
    abort with 404 if no items were found and the page was larger than
    1.  This behavor can be disabled by setting `error_out` to `False`.

    Returns an :class:`Pagination` object.
    """
    # per_page = 0 表示返回全部
    per_page = per_page and int(per_page) or 0
    if per_page == 0:
        items = cls.all()
    else:
        items = cls.limit(per_page).offset((page - 1) * per_page).all()

    # No need to count if we're on the first page and there are fewer
    # items than we expected.
    if page == 1 and len(items) < per_page:
        total = len(items)
    else:
        total = cls.order_by(None).count()
        if per_page == 0:
            per_page = total

    return Pagination(cls, page, per_page, total, items)

# --- SQLALCHEMY SUPPORT

db = SQLAlchemy()

sqlalchemy.BaseQuery.paginate = custom_paginate
# add support for custom query
orm.query.Query.paginate = custom_paginate


def drop_all():
    db.drop_all()


def create_all():
    db.create_all()


def remove_session():
    db.session.remove()

# --- SQLALCHEMY SUPPORT END


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()


class LookLively(object):
    """Ensures that MySQL connections checked out of the pool are alive."""

    def checkout(self, dbapi_con, con_record, con_proxy):
        try:
            try:
                dbapi_con.ping(False)
            except TypeError:
                dbapi_con.ping()
        except dbapi_con.OperationalError, ex:
            if ex.args[0] in (2006, 2013, 2014, 2045, 2055):
                raise exc.DisconnectionError()
            else:
                raise


def get_db_session(database_uri,
    pool_size=SQLALCHEMY_POOL_SIZE,
    pool_recycle=SQLALCHEMY_POOL_RECYCLE):

    engine = db.create_engine(
        database_uri,
        pool_size=pool_size,
        pool_recycle=pool_recycle,
        listeners=[LookLively()]
    )
    session = scoped_session(sessionmaker(bind=engine))
    dbsession = session()
    return dbsession
