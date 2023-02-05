import requests
from time import sleep, time
from enum import Enum
from models.database import DataBase
import models.parameters_db as pdb
from classes.api import APIClient, Methods
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

    def set_combustivel_ano_modelo(self, obj_ano_modelo) -> tuple:

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

        return codigo_combustivel, ano_modelo

    def tipo_combustivel(self, combustivel) -> int:
        dict = {'Gasolina': 1, 'Álcool': 2, 'Diesel': 3}
        return dict[combustivel]

    def consultar_tabela_preco(self) -> int:
        _ENDPOINT = 'ConsultarTabelaDeReferencia'
        tentativas = 1
        status = False
        while not status:
            try:
                response = self.api.request(endpoint=_ENDPOINT, method=Methods.POST.value)
                if 'Codigo' in response[0]:
                    status = True
                    return response[0]['Codigo']

                tentativas += 1

            except Exception as erro:
                tentativas += 1
                print(f'{erro} \nTentando novamente pela {tentativas}x', erro.args[0])
                if self.log_erro:
                    self.database.insert_error(endpoint=_ENDPOINT, msg_erro=erro, payload=None, code=erro.args[0])
                    continue
                sleep(tentativas * 1.5)

    def consultar_marcas(self) -> list:
        _ENDPOINT = 'ConsultarMarcas'
        tentativas = 1
        status = False

        payload = {'codigoTabelaReferencia': self.codigo_tabela_referencia,
                   'codigoTipoVeiculo': self.tipo_veiculo}
        while not status:
            try:
                response = self.api.request(endpoint=_ENDPOINT, method=Methods.POST.value, json=payload)
                status = True
                return response

            except Exception as erro:
                tentativas += 1
                print(f'{erro} \nTentando novamente pela {tentativas}x', erro.args[0])
                if self.log_erro:
                    self.database.insert_error(endpoint=_ENDPOINT, msg_erro=erro, payload=payload, code=erro.args[0])
                    continue
                sleep(tentativas * 1.5)

    def consultar_modelos(self, codigo_marca) -> list:
        _ENDPOINT = 'ConsultarModelos'
        tentativas = 1
        status = False

        payload = {'codigoTabelaReferencia': self.codigo_tabela_referencia,
                   'codigoTipoVeiculo': self.tipo_veiculo,
                   'codigoMarca': codigo_marca}

        while not status:
            try:
                response = self.api.request(endpoint=_ENDPOINT, method=Methods.POST.value, json=payload)
                if 'Modelos' in response:
                    status = True
                    return response['Modelos']

                tentativas += 1

            except Exception as erro:
                tentativas += 1
                print(f'{erro} \nTentando novamente pela {tentativas}x', erro.args[0])
                if self.log_erro:
                    self.database.insert_error(endpoint=_ENDPOINT, msg_erro=erro, payload=payload, code=erro.args[0])
                    continue
                sleep(tentativas * 1.5)

    def consultar_ano_modelo(self, codigo_marca, codigo_modelo) -> list:
        _ENDPOINT = 'ConsultarAnoModelo'
        tentativas = 1
        status = False

        payload = {'codigoTipoVeiculo': self.tipo_veiculo,
                   'codigoTabelaReferencia': self.codigo_tabela_referencia,
                   'codigoMarca': codigo_marca,
                   'codigoModelo': codigo_modelo}

        while not status:
            try:
                response = self.api.request(endpoint=_ENDPOINT, method=Methods.POST.value, json=payload)
                status = True
                return response

            except Exception as erro:
                tentativas += 1
                print(f'{erro} \nTentando novamente pela {tentativas}x', erro.args[0])
                if self.log_erro:
                    self.database.insert_error(endpoint=_ENDPOINT, msg_erro=erro, payload=payload, code=erro.args[0])
                    continue
                sleep(tentativas * 1.5)

    def consultar_valor(self, codigo_marca, codigo_modelo, obj_ano_modelo) -> list:

        _ENDPOINT = 'ConsultarValorComTodosParametros'
        tentativas = 1
        status = False

        codigo_combustivel, ano_modelo = self.set_combustivel_ano_modelo(obj_ano_modelo)
        payload = {'codigoTabelaReferencia': self.codigo_tabela_referencia, 'codigoMarca': codigo_marca,
                   'codigoModelo': codigo_modelo, 'codigoTipoVeiculo': self.tipo_veiculo,
                   'anoModelo': ano_modelo, 'codigoTipoCombustivel': codigo_combustivel,
                   'tipoVeiculo': 'caminhao',
                   'tipoConsulta': 'tradicional'}

        start = time()
        while not status:
            try:
                response = self.api.request(endpoint=_ENDPOINT, method=Methods.POST.value, json=payload)
                response['tempo_resposta'] = float(f"{(time() - start):.2f}")
                response['tentativas_requisicoes'] = tentativas
                status = True
                return response

            except Exception as erro:
                tentativas += 1
                print(f'{erro} \nTentando novamente pela {tentativas}x', erro.args[0])
                if self.log_erro:
                    self.database.insert_error(endpoint=_ENDPOINT, msg_erro=erro, payload=payload, code=erro.args[0])
                    continue
                sleep(tentativas * 1.5)

    def executar_apis(self):
        start = time()
        try:
            marcas = self.consultar_marcas()
            for marca in marcas:
                modelos = self.consultar_modelos(marca['Value'])

                for modelo in modelos:
                    list_fipes = []
                    anosModelos = self.consultar_ano_modelo(marca['Value'], modelo['Value'])

                    for anoModelo in anosModelos:
                        fipe = self.consultar_valor(marca['Value'], modelo['Value'], anoModelo)
                        print(fipe)
                        self.verify_fipe(list_fipes, fipe)

                    if len(list_fipes) > 0:
                        self.database.insert_fipe(results=list_fipes, codigo_tabela=self.codigo_tabela_referencia,
                                                  tipo_veiculo=self.tipo_veiculo)
        finally:
            self.database.close_connection()
            elapsed_time = time() - start
            seconds = int(elapsed_time % 60)
            minutes = int((elapsed_time / 60) % 60)
            hours = int(elapsed_time / 3600)
            print(f"{hours} horas, {minutes} minutos e {seconds} segundos")


# if __name__ == '__main__':
#     f = Fipe()
#     print(f.consultar_tabela_preco())
