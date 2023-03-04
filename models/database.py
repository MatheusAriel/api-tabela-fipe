from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
#from dotenv import load_dotenv
import models.parameters_db as pd

#load_dotenv()

SQLALCHEMY_DATABASE_URL_mysql = f'mysql+pymysql://{pd.user}:{pd.password}@{pd.host}:{pd.port}/{pd.database}'
engine_mysql = create_engine(SQLALCHEMY_DATABASE_URL_mysql, echo=False, pool_size=20, max_overflow=10)

Base = declarative_base()

SessionMysql = sessionmaker(bind=engine_mysql)
