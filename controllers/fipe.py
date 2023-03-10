import requests
from time import sleep, time
from models.fipe_model import FipeModel
from models.erros_fipe_model import ErrosFipeModel
from enum import Enum
from models.database import SessionMysql
from controllers.api import APIClient, Methods
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


class TipoVeiculo(Enum):
    LEVES = 1
    MOTO = 2
    PESADOS = 3


class Fipe:
    def __init__(self, tipo_veiculo=3, time_out=30, log_erro=True):
        self.url_base_api_fipe = 'https://veiculos.fipe.org.br/api/veiculos//'
        self.time_out = time_out

        self.api = APIClient(self.url_base_api_fipe, self.time_out)
        self.tipo_veiculo = tipo_veiculo
        self.log_erro = log_erro
        self.codigo_tabela_referencia = self.consultar_tabela_preco()

    def verify_fipe(self, list_fipes, response_fipe) -> None:
        if response_fipe:
            result = FipeModel.get_fipe(SessionMysql(), fipe=response_fipe['CodigoFipe'],
                                        ano_modelo=response_fipe['AnoModelo'],
                                        codigo_tabela=self.codigo_tabela_referencia)

            if result is None: list_fipes.append(response_fipe)

    def tipo_combustivel(self, combustivel) -> int:
        dict = {'Gasolina': 1, 'Álcool': 2, 'Diesel': 3}
        return dict[combustivel]

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

    def consultar_tabela_preco(self) -> int:
        endpoint = 'ConsultarTabelaDeReferencia'
        tentativas = 1
        status = False
        while not status:
            try:
                response = self.api.request(endpoint=endpoint, method=Methods.POST.value)
                if 'Codigo' in response[0]:
                    status = True
                    return response[0]['Codigo']

                tentativas += 1

            except Exception as erro:
                tentativas += 1
                logging.error(f'{erro} \nTentando novamente pela {tentativas}x - Status {erro.args[0]}')
                if self.log_erro:
                    ErrosFipeModel.insert_error(SessionMysql(), endpoint=endpoint, msg_erro=erro, payload=None,
                                                code=erro.args[0])
                sleep(tentativas * 1.5)
                continue

    def consultar_marcas(self) -> list:
        endpoint = 'ConsultarMarcas'
        tentativas = 1
        status = False

        payload = {'codigoTabelaReferencia': self.codigo_tabela_referencia,
                   'codigoTipoVeiculo': self.tipo_veiculo}
        while not status:
            try:
                response = self.api.request(endpoint=endpoint, method=Methods.POST.value, json=payload)
                status = True
                return response

            except Exception as erro:
                tentativas += 1
                logging.error(f'{erro} \nTentando novamente pela {tentativas}x - Status {erro.args[0]}')
                if self.log_erro:
                    ErrosFipeModel.insert_error(SessionMysql(), endpoint=endpoint, msg_erro=erro, payload=payload,
                                                code=erro.args[0])
                sleep(tentativas * 1.5)
                continue

    def consultar_modelos(self, codigo_marca) -> list:
        endpoint = 'ConsultarModelos'
        tentativas = 1
        status = False

        payload = {'codigoTabelaReferencia': self.codigo_tabela_referencia,
                   'codigoTipoVeiculo': self.tipo_veiculo,
                   'codigoMarca': codigo_marca}

        while not status:
            try:
                response = self.api.request(endpoint=endpoint, method=Methods.POST.value, json=payload)
                if 'Modelos' in response:
                    status = True
                    return response['Modelos']

                tentativas += 1

            except Exception as erro:
                tentativas += 1
                logging.error(f'{erro} \nTentando novamente pela {tentativas}x - Status {erro.args[0]}')
                if self.log_erro:
                    ErrosFipeModel.insert_error(SessionMysql(), endpoint=endpoint, msg_erro=erro, payload=payload,
                                                code=erro.args[0])
                sleep(tentativas * 1.5)
                continue

    def consultar_ano_modelo(self, codigo_marca, codigo_modelo) -> list:
        endpoint = 'ConsultarAnoModelo'
        tentativas = 1
        status = False

        payload = {'codigoTipoVeiculo': self.tipo_veiculo,
                   'codigoTabelaReferencia': self.codigo_tabela_referencia,
                   'codigoMarca': codigo_marca,
                   'codigoModelo': codigo_modelo}

        while not status:
            try:
                response = self.api.request(endpoint=endpoint, method=Methods.POST.value, json=payload)
                status = True
                return response

            except Exception as erro:
                tentativas += 1
                logging.error(f'{erro} \nTentando novamente pela {tentativas}x - Status {erro.args[0]}')
                if self.log_erro:
                    ErrosFipeModel.insert_error(SessionMysql(), endpoint=endpoint, msg_erro=erro, payload=payload,
                                                code=erro.args[0])
                sleep(tentativas * 1.5)
                continue

    def consultar_valor(self, codigo_marca, codigo_modelo, obj_ano_modelo) -> list:
        endpoint = 'ConsultarValorComTodosParametros'
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
                response = self.api.request(endpoint=endpoint, method=Methods.POST.value, json=payload)
                response['tempo_resposta'] = float(f"{(time() - start):.2f}")
                response['tentativas_requisicoes'] = tentativas
                status = True
                return response

            except Exception as erro:
                tentativas += 1
                logging.error(f'{erro} \nTentando novamente pela {tentativas}x - Status {erro.args[0]}')
                if self.log_erro:
                    ErrosFipeModel.insert_error(SessionMysql(), endpoint=endpoint, msg_erro=erro, payload=payload,
                                                code=erro.args[0])
                sleep(tentativas * 1.5)
                continue

    def executar_apis(self):
        i = 0
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
                        i += 1
                        logging.info(f"{fipe}, {i}")
                        self.verify_fipe(list_fipes, fipe)

                    if len(list_fipes) > 0:
                        FipeModel.insert_fipes(SessionMysql(), results=list_fipes,
                                               codigo_tabela=self.codigo_tabela_referencia,
                                               tipo_veiculo=self.tipo_veiculo)
        except Exception as err:
            logging.error(err)
        finally:
            elapsed_time = time() - start
            seconds = int(elapsed_time % 60)
            minutes = int((elapsed_time / 60) % 60)
            hours = int(elapsed_time / 3600)
            logging.info(f"{hours} horas, {minutes} minutos e {seconds} segundos - TOTAL: {i}")


if __name__ == '__main__':
    f = Fipe()
    logging.info(f.consultar_tabela_preco())
    logging.info(f.consultar_marcas())
