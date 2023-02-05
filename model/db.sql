--
-- Estrutura da tabela `fipe`
--
DROP TABLE IF EXISTS `fipe`;
CREATE TABLE IF NOT EXISTS `fipe` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `codigo_tabela_referencia` int(11) DEFAULT NULL,
  `mes_referencia` int(2) DEFAULT NULL,
  `ano_referencia` int(4) DEFAULT NULL,
  `codigo_fipe` varchar(60) DEFAULT NULL,
  `marca` varchar(100) DEFAULT NULL,
  `modelo` varchar(250) DEFAULT NULL,
  `combustivel` varchar(30) DEFAULT NULL,
  `ano_modelo` varchar(10) DEFAULT NULL,
  `preco` decimal(10,2) DEFAULT NULL,
  `categoria` enum('L','P','M') DEFAULT 'L',
  `tentativas_requisicoes` int(5) NOT NULL DEFAULT 1,
  `tempo_resposta` decimal(10,2) DEFAULT NULL COMMENT 'em segundos',
  `create_stamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
COMMIT;

--
-- Estrutura da tabela `erros_fipe`
--
DROP TABLE IF EXISTS `erros_fipe`;
CREATE TABLE IF NOT EXISTS `erros_fipe` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `endpoint` varchar(100) DEFAULT NULL,
  `code` int DEFAULT 0,
  `json` json DEFAULT NULL,
  `msg_erro` mediumtext DEFAULT NULL,
  `create_stamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
COMMIT;