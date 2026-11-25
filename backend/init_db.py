import pymysql
from sqlalchemy.engine import make_url
from config import Config


def ensure_database_exists(reset=False):
    url = make_url(Config.SQLALCHEMY_DATABASE_URI)
    database = url.database
    if not database or not database.replace('_', '').isalnum():
        raise ValueError('Use letters, numbers and underscores in the database name')
    if database.lower() in {'mysql', 'sys', 'information_schema', 'performance_schema'}:
        raise ValueError('Use a separate database for this project')
    connection = pymysql.connect(
        host=url.host or 'localhost', port=url.port or 3306,
        user=url.username, password=url.password or '', charset='utf8mb4',
    )
    try:
        with connection.cursor() as cursor:
            if reset:
                print(f'Rebuilding project database: {database}', flush=True)
                cursor.execute(f'DROP DATABASE IF EXISTS `{database}`')
            cursor.execute(f'CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        connection.commit()
    finally:
        connection.close()
