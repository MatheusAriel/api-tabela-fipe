from .database import Base
from .database import SessionMysql
from typing import List
from sqlalchemy import Column, Integer, String, DECIMAL, exc


class FipeModel(Base):
    __tablename__ = 'fipe'
    id = Column(Integer, primary_key=True)
    codigo_tabela_referencia = Column(Integer, nullable=True)
    mes_referencia = Column(Integer, nullable=True)
    ano_referencia = Column(Integer, nullable=True)
    codigo_fipe = Column(String(60), nullable=True)
    marca = Column(String(100), nullable=True)
    modelo = Column(String(250), nullable=True)
    combustivel = Column(String(30), nullable=True)
    ano_modelo = Column(String(10), nullable=True)
    preco = Column(DECIMAL, nullable=True)
    categoria = Column(String, nullable=True)
    tentativas_requisicoes = Column(Integer, nullable=False)
    tempo_resposta = Column(DECIMAL, nullable=True)

    @classmethod
    def enum_tipo_veiculo(cls, tipo_veiculo_fipe):
        tipos_veiculos = {1: 'L', 2: 'M', 3: 'P'}
        return tipos_veiculos[tipo_veiculo_fipe]

    @classmethod
    def get_mes_ano(cls, mes_referencia) -> tuple:
        meses = {'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7,
                 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12}

        try:
            ano = int(mes_referencia.split(" ")[2])
            mes = mes_referencia.split(" ")[0]
            mes = meses[mes]
        except:
            ano = 0
            mes = 0

        return ano, mes

    def insert_fipes(db: SessionMysql, **kwargs) -> bool:
        try:
            objs = []
            for fipe in kwargs.get('results'):
                ano, mes = FipeModel.get_mes_ano(fipe['MesReferencia'])
                obj = FipeModel(
                    codigo_tabela_referencia=kwargs.get('codigo_tabela'),
                    mes_referencia=mes,
                    ano_referencia=ano,
                    codigo_fipe=fipe['CodigoFipe'],
                    marca=fipe['Marca'],
                    modelo=fipe['Modelo'],
                    combustivel=fipe['Combustivel'],
                    ano_modelo=fipe['AnoModelo'] if fipe['AnoModelo'] != 32000 else '0 KM',
                    preco=fipe['Valor'].replace('R$ ', '').replace('.', '').replace(',', '.'),
                    categoria=FipeModel.enum_tipo_veiculo(kwargs.get('tipo_veiculo')),
                    tentativas_requisicoes=fipe['tentativas_requisicoes'],
                    tempo_resposta=fipe['tempo_resposta']
                )
                objs.append(obj)

            db.bulk_save_objects(objs)
            db.commit()
            return True

        except exc.SQLAlchemyError as err:
            print('Erro DB: ', err)
            return False

        finally:
            db.close()

    def get_fipe(db: SessionMysql, **kwargs) -> None | List:
        try:
            ano_modelo = kwargs.get('ano_modelo') if kwargs.get('ano_modelo') != 32000 else '0 KM'

            return db.query(FipeModel.id). \
                filter(FipeModel.codigo_fipe == kwargs.get('fipe')). \
                filter(FipeModel.ano_modelo == ano_modelo). \
                filter(FipeModel.codigo_tabela_referencia == kwargs.get('codigo_tabela')). \
                first()

        except exc.SQLAlchemyError as err:
            print('Erro DB: ', err)
            return None

        finally:
            db.close()
