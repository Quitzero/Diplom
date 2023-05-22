from sqlalchemy.orm import sessionmaker
from src.models import Poly


def read_satellites(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    poly = session.query(Poly.Data_Collection).distinct().all()

    return poly
    
def read_table(engine, dataset_satellite, cloudiness_min , cloudiness_max, date_from, date_to):
    Session = sessionmaker(bind=engine)
    session = Session()
    if date_from ==  None or date_to == None:
        table_data = session.query(Poly).filter(Poly.Data_Collection== f'{dataset_satellite}', 
                                            cloudiness_min<= Poly.Cloud_Cover, 
                                            Poly.Cloud_Cover <= cloudiness_max,
                                            ).all()
    else:
        table_data = session.query(Poly).filter(Poly.Data_Collection== f'{dataset_satellite}', 
                                            cloudiness_min<= Poly.Cloud_Cover, 
                                            Poly.Cloud_Cover <= cloudiness_max,
                                            date_from <= Poly.Time_Range,
                                            Poly.Time_Range <= date_to
                                            ).all()

    return table_data

def read_dd(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    dd = session.query(Poly.id).all()
    print(dd)