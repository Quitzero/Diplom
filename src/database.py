from sqlalchemy import create_engine
import sqlalchemy
import configparser


def connect_tp_db(Username, UserPassword):
    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read("src/db.ini")  # читаем конфиг
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'.format(Username, UserPassword, config["Database"]["HOSTNAME"], config["Database"]["DATABASE"])

    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        #connection = engine.connect()
    except sqlalchemy.exc.OperationalError:
        return False, None
    else:
        return True, engine