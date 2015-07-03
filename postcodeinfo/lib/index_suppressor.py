from django import db
import logging


class IndexSuppressor(object):

    def __init__(self, tablename, cursor=db.connection.cursor()):
        self.cursor = cursor
        self.tablename = tablename
        self.index_cache = []

    def __enter__(self):
        logging.debug( '__enter__' )
        self._drop_indexes()

    def __exit__(self, type, value, tb):
        logging.debug( '__exit__' )
        self._restore_indexes()

    def _indexes_on(self, tablename):
        sql = ("SELECT indexname, indexdef "
               "from pg_indexes "
               "where tablename = %s "
               "and NOT(indexdef like %s)")

        self.cursor.execute(sql, [tablename, '% UNIQUE %'])
        return self.cursor.fetchall()

    def _drop_indexes(self):
        for index in self._indexes_on(self.tablename):
            logging.debug(
                'dropping index {idx}'.format(idx=index[0]))
            self.cursor.execute('DROP INDEX {idx}'.format(idx=index[0]))
            self.index_cache.append(index)

    def _restore_indexes(self):
        for index in self.index_cache:
            logging.debug('restoring index {idx}'.format(idx=index[0]))
            self.cursor.execute(index[1])
