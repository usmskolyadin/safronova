"""SQLite backend used when the stdlib sqlite3 module has been swapped for
pysqlite3-binary (see the patch in settings.py and DEPLOY_SPRINTHOST.md).

pysqlite3's Connection doesn't implement getlimit()/setlimit(), which
Django's stock sqlite3 backend calls to read SQLITE_MAX_VARIABLE_NUMBER.
Rather than monkeypatching the (immutable, C-level) Connection type, this
overrides the feature class with the conservative static value Django
itself hardcoded here before it switched to dynamic detection.
"""

from django.db.backends.sqlite3.base import DatabaseWrapper as SqliteDatabaseWrapper
from django.db.backends.sqlite3.features import DatabaseFeatures as SqliteDatabaseFeatures


class DatabaseFeatures(SqliteDatabaseFeatures):
    max_query_params = 999


class DatabaseWrapper(SqliteDatabaseWrapper):
    features_class = DatabaseFeatures
