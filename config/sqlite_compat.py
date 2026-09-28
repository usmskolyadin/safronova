"""Compatibility shims for hosts where sqlite3 has been swapped for
pysqlite3-binary (see the patch in settings.py and DEPLOY_SPRINTHOST.md).

pysqlite3 is missing two things the stdlib sqlite3 gained in Python 3.11+
that Django's SQLite backend relies on, from more than one call site each:

1. The SQLITE_LIMIT_* module-level constants.
2. Connection.getlimit() / .setlimit().

Importing this module patches both in, wherever Django happens to look
for them, so it doesn't matter which specific call site Django uses.
"""

import sqlite3

# Real SQLite C API values (sqlite3.h) — stable across SQLite versions.
_LIMIT_CONSTANTS = {
    'SQLITE_LIMIT_LENGTH': 0,
    'SQLITE_LIMIT_SQL_LENGTH': 1,
    'SQLITE_LIMIT_COLUMN': 2,
    'SQLITE_LIMIT_EXPR_DEPTH': 3,
    'SQLITE_LIMIT_COMPOUND_SELECT': 4,
    'SQLITE_LIMIT_VDBE_OP': 5,
    'SQLITE_LIMIT_FUNCTION_ARG': 6,
    'SQLITE_LIMIT_ATTACHED': 7,
    'SQLITE_LIMIT_LIKE_PATTERN_LENGTH': 8,
    'SQLITE_LIMIT_VARIABLE_NUMBER': 9,
    'SQLITE_LIMIT_TRIGGER_DEPTH': 10,
    'SQLITE_LIMIT_WORKER_THREADS': 11,
}

for _module in (sqlite3, getattr(sqlite3, 'dbapi2', None)):
    if _module is None:
        continue
    for _name, _value in _LIMIT_CONSTANTS.items():
        if not hasattr(_module, _name):
            setattr(_module, _name, _value)


class CompatConnection(sqlite3.Connection):
    # 999 is the conservative value Django itself hardcoded for
    # SQLITE_LIMIT_VARIABLE_NUMBER before it switched to reading the real
    # compiled limit dynamically; safe for every category even if the
    # true limit is higher — Django just batches a bit more eagerly.
    def getlimit(self, category):
        return 999

    def setlimit(self, category, value):
        return 999
