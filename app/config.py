import os

if 'DEBUG' in os.environ:
    print('[Debug] development mode')

    from dotenv import load_dotenv

    cur_path = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(cur_path, os.pardir, '.env')
    load_dotenv(dotenv_path=env_path)

    os.environ['DB_SERVER'] = '127.0.0.1'
else:
    print('[Debug] production mode')

VERSION = os.environ['VERSION']
SECRET_KEY = os.environ['SECRET_KEY']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_SERVER = os.environ['DB_SERVER']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']
SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
    DB_USER, DB_PASS, DB_SERVER, DB_PORT, DB_NAME
)
