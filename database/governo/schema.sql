-- ============================================================
-- Banco da API governamental SIMULADA: governo_simulado
-- Separado do banco da clínica (cada serviço tem a sua persistência).
-- Esqueleto inicial: ajustem na Semana 4 conforme a integração.
-- ============================================================

CREATE DATABASE IF NOT EXISTS governo_simulado
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE governo_simulado;

CREATE TABLE IF NOT EXISTS animal_registrado (
  id_registro         INT AUTO_INCREMENT PRIMARY KEY,
  id_animal_clinica   INT          NOT NULL,      -- id do animal no sistema da clínica
  nome                VARCHAR(80)  NOT NULL,
  especie             VARCHAR(60)  NOT NULL,
  raca                VARCHAR(80)  NULL,
  numero_microchip    VARCHAR(15)  NULL,
  protocolo           VARCHAR(60)  NOT NULL,
  data_registro       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  data_atualizacao    DATETIME     NULL,
  CONSTRAINT uk_gov_animal_clinica UNIQUE (id_animal_clinica),
  CONSTRAINT uk_gov_animal_protocolo UNIQUE (protocolo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS vacina_antirrabica_registrada (
  id_registro_vacina  INT AUTO_INCREMENT PRIMARY KEY,
  id_registro         INT          NOT NULL,
  id_vacina_clinica   INT          NOT NULL,      -- id da vacina no sistema da clínica
  data_aplicacao      DATE         NOT NULL,
  lote                VARCHAR(50)  NULL,
  protocolo           VARCHAR(60)  NOT NULL,
  data_registro       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uk_gov_vacina_clinica UNIQUE (id_vacina_clinica),
  CONSTRAINT uk_gov_vacina_protocolo UNIQUE (protocolo),
  CONSTRAINT fk_gov_vacina_animal FOREIGN KEY (id_registro) REFERENCES animal_registrado (id_registro)
) ENGINE=InnoDB;

-- Idempotência: se a clínica reenviar a mesma operação, devolvemos o mesmo protocolo.
CREATE TABLE IF NOT EXISTS operacao_recebida (
  chave_idempotencia  VARCHAR(100) PRIMARY KEY,
  protocolo           VARCHAR(60)  NOT NULL,
  data_recebimento    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
