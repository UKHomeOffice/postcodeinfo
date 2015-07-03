# -*- coding: utf-8 -*-
from django import db
import logging


# We have to do this manually, rather than SET CONSTRAINTS DEFERRED,
# because:
# - when we import the whole of AddressBase we have to do it
#   file-by-file
# - we can't do it all in one transaction because it will be
#   way too slow, because:
# - the \copy cmd, which is by several orders-of-magnitude the fastest
#   way to get large amts of data into Postgres, messes with the
#   transaction structure
# - Postgres behaves better with a manageable transaction size, rather
#   than trying to do the whole ~30M rows in one
# So, this context mgr will explicitly


class IndexSuppressor(object):

    def __init__(self, tablename, cursor=db.connection.cursor()):
        self.cursor = cursor
        self.tablename = tablename
        self.index_cache = []

    def __enter__(self):
        logging.debug('__enter__')
        self._drop_indexes()

    def __exit__(self, type, value, tb):
        logging.debug('__exit__')
        self._restore_indexes()

    def _indexes_on(self, tablename):
        # NOTE: we have to exclude the UNIQUE indexes
        # because there are constraints etc which depend on them,
        # and we dont' get visibility of those relationships
        # so we can't safely drop-then-recreate them
        sql = ("SELECT indexname, indexdef "
               "from pg_indexes "
               "where tablename = %s "
               "and NOT(indexdef like %s)"
               )

        self.cursor.execute(sql, [tablename, '% UNIQUE %'])
        return self.cursor.fetchall()

    def _drop_indexes(self):
        for index in self._indexes_on(self.tablename):
            logging.debug(
                'dropping index {idx}'.format(idx=index[0]))

            self.cursor.execute(
                'DROP INDEX {idx} CASCADE'.format(idx=index[0]))
            self.index_cache.append(index)

    def _restore_indexes(self):
        for index in self.index_cache:
            logging.debug('restoring index {idx}'.format(idx=index[0]))
            self.cursor.execute(index[1])
