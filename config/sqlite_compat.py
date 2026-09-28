"""Connection factory for hosts where sqlite3 has been swapped for
pysqlite3-binary (see the patch in settings.py and DEPLOY_SPRINTHOST.md).

pysqlite3's Connection doesn't implement getlimit()/setlimit() (only added
to the stdlib sqlite3 in Python 3.11), and Django's SQLite backend calls
them directly from several places, not just one — so patching a single
call site keeps missing the next one. This subclasses Connection to
provide both methods, so every call site just works, no matter which one
Django happens to use.
"""

import sqlite3


class CompatConnection(sqlite3.Connection):
    # 999 is the conservative value Django itself hardcoded for
    # SQLITE_LIMIT_VARIABLE_NUMBER before it switched to reading the real
    # compiled limit dynamically; safe even if the true limit is higher.
    def getlimit(self, category):
        return 999

    def setlimit(self, category, value):
        return 999
