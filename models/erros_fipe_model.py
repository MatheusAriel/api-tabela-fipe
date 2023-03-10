from .database import Base
from .database import SessionMysql
import json
from sqlalchemy import Column, Integer, String, JSON, exc, Text


class ErrosFipeModel(Base):
    __tablename__ = 'erros_fipe'
    id = Column(Integer, primary_key=True)
    endpoint = Column(String(100), nullable=True)
    json = Column(JSON, nullable=True)
    msg_erro = Column(Text(), nullable=True)
    code = Column(Integer, nullable=True)

    def insert_error(db: SessionMysql, endpoint, msg_erro, payload=None, code=0) -> bool:
        try:
            obj = ErrosFipeModel(
                endpoint=endpoint,
                msg_erro=str(msg_erro),
                json=json.dumps(payload) if payload is not None else None,
                code=code
            )
            db.add(obj)
            db.commit()
            return True

        except exc.SQLAlchemyError as err:
            print('Erro DB: ', err)
            return False
        finally:
            db.close()
