from sqlalchemy import create_engine
import sqlalchemy


def connect_tp_db(Username, UserPassword):
    HOSTNAME = 'localhost'
    DATABASE = 'usersdb'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'.format(Username, UserPassword, HOSTNAME, DATABASE)

    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        connection = engine.connect()
    except sqlalchemy.exc.OperationalError:
        print("Database doesn't exists or username/password incorrect")
        return False, None
    else:
        print("Connection successful")
        return True, engine