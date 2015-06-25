import boto

from django.conf import settings

from boto.s3.key import Key

class S3Adapter(object):

    def __init__(self, connection=None, bucket=None):
        self.connection = connection
        if connection is None:
            self.connection = self.connect()

        self.bucket = bucket
        if bucket is None:
            self.bucket = self.get_bucket()

    def connect(self, region_name=settings.AWS['region_name']): 
        return boto.s3.connect_to_region(region_name) 
 
    def get_bucket(self, bucket_name=settings.AWS['s3_bucket_name']): 
        return self.connection.get_bucket(bucket_name) 
 
    def key(self, url): 
        return url.split('/')[-1]
 
    def file(self, key): 
        return self.bucket.get_key(key) 
 
    def download(self, s3_object, local_file_path): 
        s3_object.get_contents_to_filename(local_file_path) 
        return local_file_path
 
    def upload(self, local_file_path, s3_key): 
        k = Key(self.bucket) 
        k.key = s3_key 
        return k.set_contents_from_filename(local_file_path) 