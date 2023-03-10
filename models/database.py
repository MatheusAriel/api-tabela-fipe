from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

user = os.getenv('FIPE_MYSQL_USER')
password = os.getenv('FIPE_MYSQL_PASSWORD')
host = os.getenv('FIPE_MYSQL_HOST')
port = os.getenv('FIPE_MYSQL_PORT')
database = os.getenv('FIPE_MYSQL_DATABASE')

SQLALCHEMY_DATABASE_URL_mysql = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
engine_mysql = create_engine(SQLALCHEMY_DATABASE_URL_mysql, echo=False, pool_size=20, max_overflow=10)

Base = declarative_base()

SessionMysql = sessionmaker(bind=engine_mysql)
