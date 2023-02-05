import requests
from time import sleep, time
from enum import Enum
from model.database import DataBase
import model.parameters_db as pdb
from api import APIClient, Methods
import json


class TipoVeiculo(Enum):
    LEVES = 1
    MOTO = 2
    PESADOS = 3


class Fipe:
    def __init__(self, tipo_veiculo=3, time_out=30, log_erro=True):
        self.url_base_api_fipe = 'https://veiculos.fipe.org.br/api/veiculos//'
        self.time_out = time_out

        self.api = APIClient(self.url_base_api_fipe, None, self.time_out)
        self.database = DataBase(pdb.host, pdb.user, pdb.password, pdb.database)
        self.tipo_veiculo = tipo_veiculo
        self.log_erro = log_erro
        self.codigo_tabela_referencia = self.consultar_tabela_preco()

    def verify_fipe(self, list_fipes, response_fipe) -> None:
        if response_fipe:
            if len(self.database.get_fipe(fipe=response_fipe['CodigoFipe'], ano_modelo=response_fipe['AnoModelo'],
                                          codigo_tabela=self.codigo_tabela_referencia)) <= 0:
                list_fipes.append(response_fipe)

    def set_combustivel_ano_modelo(self, obj_ano_modelo) -> dict:

        try:
            combustivel = obj_ano_modelo['Label'].split(" ")[1]
            codigo_combustivel = self.tipo_combustivel(combustivel)
            ano_modelo = obj_ano_modelo['Label'].split(" ")[0]
        except:
            if self.tipo_veiculo == 3:
                # CAMINHAO
                codigo_combustivel = 3  # DIESEL - DEFAULT
                ano_modelo = obj_ano_modelo['Label']
            else:
                # CARRO E MOTO
                codigo_combustivel = 1  # GASOLINA - DEFAULT
                ano_modelo = obj_ano_modelo['Label']

        return {'codigo_combustivel': codigo_combustivel, 'ano_modelo': ano_modelo}

    def tipo_combustivel(self, combustivel) -> int:
        dict = {'Gasolina': 1, 'Álcool': 2, 'Diesel': 3}
        return dict[combustivel]

    def consultar_tabela_preco(self) -> int:
        _ENDPOINT = 'ConsultarTabelaDeReferencia'
        tentativas = 1
        status = False
        while not status:
            try:
                response = self.api.request(_ENDPOINT, Methods.POST.value)
                if not 'erro' in response or 'Codigo':
                    status = True
                    return response[0]['Codigo']

                tentativas += 1

            except Exception as erro:
                tentativas += 1
                print(f'{erro} \nTentando novamente pela {tentativas}x', erro.args[0])
                sleep(tentativas * 1.5)
                if self.log_erro:
                    self.database.insert_error(_ENDPOINT, erro, None, erro.args[0])
                    continue




if __name__ == '__main__':
    f = Fipe()
    print(f.consultar_tabela_preco())
