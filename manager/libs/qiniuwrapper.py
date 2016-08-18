# -*- coding:utf-8 -*-
from qiniu import Auth, put_file, put_stream, BucketManager, build_batch_delete
from manager.settings.last_settings import QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET_NAME


class QiniuWrapper():

    policy = {'returnBody': '{"key": $(key), "type": $(mimeType), "name": $(fname), "size": $(fsize), "hash": $(etag)}'}
    bucket_name = QINIU_BUCKET_NAME
    domain = 'http://%s.qiniudn.com/' % bucket_name

    def __init__(self):
        self.q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
        self.bucket_manager = BucketManager(self.q)

    def get_upload_token(self, key, expires=3600):
        return self.q.upload_token(self.bucket_name, key, expires, self.policy)

    def upload_file(self, key, filename, mime_type="application/octet-stream"):
        '''
        上传文件到七牛，如果指定的key对应的文件在七牛上已经存在, 会覆盖原来七牛上的文件
        '''
        ret, info = put_file(self.get_upload_token(key), key, filename, mime_type=mime_type, check_crc=True)
        if info.status_code != 200:
            return (False, info)
        return (True, info)

    def upload_stream(self, key, input_stream, data_size, mime_type="application/octet-stream"):
        '''
        上传文件到七牛，如果指定的key对应的文件在七牛上已经存在, 会覆盖原来七牛上的文件
        '''
        ret, info = put_stream(self.get_upload_token(key), key, input_stream, data_size, mime_type=mime_type, check_crc=True)
        if info.status_code != 200:
            return (False, info)
        return (True, info)

    def move(self, old_key, new_key):
        ret, info = self.bucket_manager.move(self.bucket_name, old_key, self.bucket_name, new_key)
        if info.status_code != 200:
            return (False, info)
        return (True, info)

    def delete(self, key):
        ret, info = self.bucket_manager.delete(self.bucket_name, key)
        if info.status_code != 200:
            return (False, info)
        return (True, info)

    def batch_delete(self, keys):
        '''
        keys = ['key1', 'key2', 'key3']
        '''
        ops = build_batch_delete(self.bucket_name, keys)
        ret, info = self.bucket_manager.batch(ops)
        if info.status_code != 200:
            return (False, info)
        return (True, info)

    def list(self, prefix=None, limit=1000, marker=None):
        return self.bucket_manager.list(self.bucket_name, prefix=prefix, marker=marker, limit=limit)

    @classmethod
    def get_url(cls, key):
        return cls.domain + key
