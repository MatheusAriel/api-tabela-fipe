from fipe import Fipe, TipoVeiculo

fipe = Fipe(tipo_veiculo=TipoVeiculo.LEVES.value, time_out=300, log_erro=False)
fipe.executar_apis()
