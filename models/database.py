import mysql.connector
import json


class DataBase:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

        self.cursor = self.connection.cursor()
        self.count = 1

    def close_connection(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()

    def get_mes_ano(self, mes_referencia) -> tuple:

        meses = {'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12}

        try:
            ano = int(mes_referencia.split(" ")[2])
            mes = mes_referencia.split(" ")[0]
            mes = meses[mes]
        except:
            ano = 0
            mes = 0

        return ano, mes

    def enum_tipo_veiculo(self, tipo_veiculo_fipe):
        dict = {1: 'L', 2: 'M', 3: 'P'}
        return dict[tipo_veiculo_fipe]

    def insert_fipe(self, **kwargs) -> bool:
        try:
            for result in kwargs.get('results'):
                preco = result['Valor'].replace('R$ ', '')
                preco = preco.replace('.', '')
                preco = preco.replace(',', '.')

                categoria = self.enum_tipo_veiculo(kwargs.get('tipo_veiculo'))
                ano_modelo = result['AnoModelo'] if result['AnoModelo'] != 32000 else '0 KM'
                query = """INSERT INTO fipe (codigo_fipe, marca, modelo, ano_modelo, preco, mes_referencia, ano_referencia, 
                    combustivel, codigo_tabela_referencia, categoria, tentativas_requisicoes, tempo_resposta) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

                mes, ano = self.get_mes_ano(result['MesReferencia'])
                values = (
                    result['CodigoFipe'], result['Marca'], result['Modelo'], ano_modelo, preco, mes,
                    ano, result['Combustivel'], kwargs.get('codigo_tabela'), categoria,
                    result['tentativas_requisicoes'], result['tempo_resposta'])

                self.cursor.execute(query, values)
                self.connection.commit()
                # print(f"Inserido: {self.count} - \t{result}")
                self.count += 1

        except mysql.connector.Error as err:
            print('Erro DB: ', err)
            print("Error Code:", err.errno)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)
            return False
        else:
            return True

    def get_fipe(self, **kwargs) -> list:
        try:
            ano_modelo = kwargs.get('ano_modelo') if kwargs.get('ano_modelo') != 32000 else '0 KM'
            query = """SELECT * FROM `fipe` WHERE `codigo_fipe`=%s AND `ano_modelo`=%s AND`codigo_tabela_referencia`=%s LIMIT 1"""
            values = (kwargs.get('fipe'), ano_modelo, kwargs.get('codigo_tabela'))
            self.cursor.execute(query, values)
            return self.cursor.fetchall()


        except mysql.connector.Error as err:
            print('Erro DB: ', err)
            print("Error Code:", err.errno)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)

    def insert_error(self, endpoint, msg_erro, payload=None, code=0) -> bool:
        try:
            print(endpoint, msg_erro, payload, code)
            j = payload
            if j is not None:
                j = json.dumps(payload)

            print(endpoint, code, j, str(msg_erro))
            query = """INSERT INTO erros_fipe (endpoint, code, json, msg_erro) VALUES (%s, %s, %s, %s) """
            values = (endpoint, code, j, str(msg_erro))

            self.cursor.execute(query, values)
            self.connection.commit()

        except mysql.connector.Error as err:
            print('Erro DB: ', err)
            print("Error Code:", err.errno)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)
            return False
        else:
            return True

    def get_errors(self, status='N') -> list:
        try:

            query = """SELECT * FROM `erros_fipe` WHERE status=%s"""
            values = (status,)
            self.cursor.execute(query, values)
            return self.cursor.fetchall()

        except mysql.connector.Error as err:
            print('Erro DB: ', err)
            print("Error Code:", err.errno)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)

    def change_status_errors(self, id, status='Y') -> bool:
        try:
            query = """UPDATE erros_fipe SET status=%s WHERE id=%s """
            values = (status, id)

            self.cursor.execute(query, values)
            self.connection.commit()


        except mysql.connector.Error as err:
            print('Erro DB: ', err)
            print("Error Code:", err.errno)
            print("SQLSTATE", err.sqlstate)
            print("Message", err.msg)
            return False
        else:
            return True
