from controllers.fipe import Fipe, TipoVeiculo
from time import sleep

fipe_leves = Fipe(tipo_veiculo=TipoVeiculo.PESADOS.value, time_out=300, log_erro=True)
fipe_leves.executar_apis()
sleep(1200)  # 20 minutos

fipe_pesados = Fipe(tipo_veiculo=TipoVeiculo.LEVES.value, time_out=300, log_erro=True)
fipe_pesados.executar_apis()
sleep(1200)  # 20 minutos

fipe_motos = Fipe(tipo_veiculo=TipoVeiculo.MOTO.value, time_out=300, log_erro=True)
fipe_motos.executar_apis()
