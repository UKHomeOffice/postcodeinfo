from postcode_api.models import CacheVersion


# The CACHES setting KEY_FUNCTION will specify this as the
# function to call whenever it's constructing a cache key
# The dynamic CacheVersion call means that we can easily
# invalidate the whole cache by incrementing the version in
# the DB, and it will be picked up straight away by all the
# servers in the auto-scaling group (which is more tricky to
# achieve with shell commands)
def make_key(key, key_prefix, version):
    return ':'.join([key_prefix, CacheVersion.objects.latest_as_string(), key])
