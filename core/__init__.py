import os

# When using PyMySQL as the MySQL driver, make it compatible with MySQLdb
if os.getenv('DB_ENGINE', '').lower() == 'mysql':
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except Exception:
        # PyMySQL not installed or other issue; Django will raise a clear error on DB connect
        pass