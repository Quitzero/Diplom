from sqlalchemy.orm import sessionmaker
from src.models import Poly


def read_satellites(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    poly = session.query(Poly.Data_Collection).distinct().all()

    return poly
    