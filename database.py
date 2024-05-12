from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, create_engine, DateTime


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True)
    long_name = Column(String)
    short_name = Column(String)
    macaddr = Column(String)
    hw_model = Column(String)
    inserted_at = Column(DateTime, default=datetime.now)

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    text = Column(String)
    inserted_at = Column(DateTime, default=datetime.now)

class Position(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    lat_lon = Column(String)
    inserted_at = Column(DateTime, default=datetime.now)

class Telemetry(Base):
    __tablename__ = 'telemetries'

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    battery_level = Column(Integer)
    voltage = Column(Float)
    # channel_utilization = Column(Float, nullable=True)
    air_util_tx = Column(Float)
    rx_snr = Column(Float)
    hop_limit = Column(Integer)
    rx_rssi = Column(Integer)
    inserted_at = Column(DateTime, default=datetime.now)


engine = create_engine('sqlite:///meshtastic.db')
Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
session = Session()

def add_user(user_id, longName, shortName, macaddr, hwModel):
    user = User(user_id=user_id,
                long_name=longName,
                short_name=shortName,
                macaddr=macaddr,
                hw_model=hwModel
    )
    session.add(user)
    session.commit()

def add_message(user_id, text):
    text = Message(user_id=user_id, text=text)
    session.add(text)
    session.commit()

def add_position(user_id, lat_lon):
    position = Position(user_id=user_id, lat_lon=lat_lon)
    session.add(position)
    session.commit()

def user_exists(user_id):
    user = session.query(User).filter_by(user_id=user_id).first()
    return user is not None

def add_telemetry(fromId_hex, batteryLevel, voltage, airUtilTx, rxSnr, hopLimit, rxRssi):
    telemetry = Telemetry(user_id=fromId_hex, 
                          battery_level=batteryLevel, 
                          voltage=voltage,  
                          air_util_tx = airUtilTx,
                          rx_snr = rxSnr,
                          hop_limit = hopLimit,
                          rx_rssi = rxRssi
    )
    session.add(telemetry)
    session.commit()