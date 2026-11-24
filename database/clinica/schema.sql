-- ============================================================
-- Banco da clínica: clinica_veterinaria (MariaDB / XAMPP)
-- Baseado no DER "A3 DER - Clínica Veterinária".
--
-- Seguro para rodar mais de uma vez: usa IF NOT EXISTS, então
-- NÃO altera tabelas que já existem (endereco, tutor, especie...).
-- Se alguma tabela já criada estiver diferente deste script,
-- ajustem em grupo e atualizem este arquivo.
-- ============================================================

CREATE DATABASE IF NOT EXISTS clinica_veterinaria
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE clinica_veterinaria;

-- ---------------------- CADASTRO ----------------------

CREATE TABLE IF NOT EXISTS endereco (
  id_endereco  INT AUTO_INCREMENT PRIMARY KEY,
  cep          CHAR(8)      NOT NULL,
  logradouro   VARCHAR(150) NOT NULL,
  numero       VARCHAR(10)  NOT NULL,
  complemento  VARCHAR(80)  NULL,
  bairro       VARCHAR(80)  NOT NULL,
  cidade       VARCHAR(80)  NOT NULL,
  uf           CHAR(2)      NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tutor (
  id_tutor       INT AUTO_INCREMENT PRIMARY KEY,
  nome_completo  VARCHAR(150) NOT NULL,
  cpf            CHAR(11)     NOT NULL,
  dt_nasc        DATE         NULL,
  email          VARCHAR(120) NULL,
  telefone       VARCHAR(20)  NULL,
  id_endereco    INT          NOT NULL,
  data_cadastro  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ativo          TINYINT(1)   NOT NULL DEFAULT 1,
  CONSTRAINT uk_tutor_cpf UNIQUE (cpf),
  CONSTRAINT fk_tutor_endereco FOREIGN KEY (id_endereco) REFERENCES endereco (id_endereco)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS especie (
  id_especie  INT AUTO_INCREMENT PRIMARY KEY,
  nome        VARCHAR(60)  NOT NULL,
  descricao   VARCHAR(255) NULL,
  ativo       TINYINT(1)   NOT NULL DEFAULT 1,
  CONSTRAINT uk_especie_nome UNIQUE (nome)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS raca (
  id_raca     INT AUTO_INCREMENT PRIMARY KEY,
  nome        VARCHAR(80)  NOT NULL,
  id_especie  INT          NOT NULL,
  descricao   VARCHAR(255) NULL,
  ativo       TINYINT(1)   NOT NULL DEFAULT 1,
  CONSTRAINT uk_raca_especie_nome UNIQUE (id_especie, nome),
  -- necessário para a FK composta de animal (raça pertence à espécie)
  CONSTRAINT uk_raca_id_especie UNIQUE (id_raca, id_especie),
  CONSTRAINT fk_raca_especie FOREIGN KEY (id_especie) REFERENCES especie (id_especie)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS animal (
  id_animal   INT AUTO_INCREMENT PRIMARY KEY,
  nome        VARCHAR(80)  NOT NULL,
  id_especie  INT          NOT NULL,
  id_raca     INT          NOT NULL,   -- use a raça "SRD" quando não definida
  sexo        ENUM('M','F') NOT NULL,
  dt_nasc     DATE         NULL,
  porte       ENUM('PEQUENO','MEDIO','GRANDE') NULL,
  id_tutor    INT          NOT NULL,
  observacao  TEXT         NULL,
  ativo       TINYINT(1)   NOT NULL DEFAULT 1,
  CONSTRAINT fk_animal_tutor   FOREIGN KEY (id_tutor)   REFERENCES tutor (id_tutor),
  CONSTRAINT fk_animal_especie FOREIGN KEY (id_especie) REFERENCES especie (id_especie),
  -- garante que a raça pertence à espécie escolhida
  CONSTRAINT fk_animal_raca_especie FOREIGN KEY (id_raca, id_especie) REFERENCES raca (id_raca, id_especie)
) ENGINE=InnoDB;

-- ------------------- ATENDIMENTO CLÍNICO -------------------

CREATE TABLE IF NOT EXISTS veterinario (
  id_veterinario    INT AUTO_INCREMENT PRIMARY KEY,
  nome_completo     VARCHAR(150) NOT NULL,
  cpf               CHAR(11)     NOT NULL,
  crmv              VARCHAR(20)  NOT NULL,
  uf_crmv           CHAR(2)      NOT NULL,
  email             VARCHAR(120) NOT NULL,
  telefone          VARCHAR(20)  NULL,
  senha_hash        VARCHAR(255) NOT NULL,
  email_confirmado  TINYINT(1)   NOT NULL DEFAULT 0,
  ativo             TINYINT(1)   NOT NULL DEFAULT 1,
  ultimo_acesso     DATETIME     NULL,
  data_cadastro     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uk_vet_cpf   UNIQUE (cpf),
  CONSTRAINT uk_vet_email UNIQUE (email),
  CONSTRAINT uk_vet_crmv  UNIQUE (crmv, uf_crmv)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS consulta (
  id_consulta     INT AUTO_INCREMENT PRIMARY KEY,
  id_animal       INT          NOT NULL,
  id_veterinario  INT          NOT NULL,
  data_hora       DATETIME     NOT NULL,
  motivo          VARCHAR(255) NOT NULL,
  historico       TEXT         NULL,
  sintomas        TEXT         NULL,
  diagnostico     TEXT         NULL,
  tratamento      TEXT         NULL,
  status          ENUM('AGENDADA','EM_ATENDIMENTO','CONCLUIDA','CANCELADA') NOT NULL DEFAULT 'AGENDADA',
  CONSTRAINT fk_consulta_animal FOREIGN KEY (id_animal)      REFERENCES animal (id_animal),
  CONSTRAINT fk_consulta_vet    FOREIGN KEY (id_veterinario) REFERENCES veterinario (id_veterinario)
) ENGINE=InnoDB;

-- Uma linha = uma vacinação efetivamente aplicada.
CREATE TABLE IF NOT EXISTS vacina (
  id_vacina          INT AUTO_INCREMENT PRIMARY KEY,
  id_animal          INT          NOT NULL,
  id_veterinario     INT          NOT NULL,
  nome_vacina        VARCHAR(100) NOT NULL,
  antirrabica        TINYINT(1)   NOT NULL DEFAULT 0,  -- 1 = vai para a API governamental
  fabricante         VARCHAR(100) NULL,
  lote               VARCHAR(50)  NULL,
  data_aplicacao     DATE         NOT NULL,
  dose               VARCHAR(30)  NULL,
  via_administracao  VARCHAR(30)  NULL,
  proxima_dose       DATE         NULL,
  observacao         TEXT         NULL,
  CONSTRAINT fk_vacina_animal FOREIGN KEY (id_animal)      REFERENCES animal (id_animal),
  CONSTRAINT fk_vacina_vet    FOREIGN KEY (id_veterinario) REFERENCES veterinario (id_veterinario)
) ENGINE=InnoDB;

-- Histórico de microchips: nunca apagar, apenas desvincular (ativo = 0).
CREATE TABLE IF NOT EXISTS vinculo_microchip (
  id_vinculo          INT AUTO_INCREMENT PRIMARY KEY,
  id_animal           INT          NOT NULL,
  id_veterinario      INT          NOT NULL,
  numero_microchip    VARCHAR(15)  NOT NULL,
  data_vinculacao     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  data_desvinculacao  DATETIME     NULL,
  ativo               TINYINT(1)   NOT NULL DEFAULT 1,
  observacao          TEXT         NULL,
  -- colunas auxiliares: valem o id/número só quando o vínculo está ativo (senão NULL),
  -- assim o UNIQUE impede dois vínculos ativos conflitantes.
  -- "STORED" (em vez de "PERSISTENT") funciona tanto no MariaDB quanto no MySQL.
  animal_ativo  INT         AS (IF(ativo = 1, id_animal, NULL)) STORED,
  chip_ativo    VARCHAR(15) AS (IF(ativo = 1, numero_microchip, NULL)) STORED,
  CONSTRAINT uk_microchip_numero UNIQUE (numero_microchip),
  CONSTRAINT uk_um_vinculo_ativo_por_animal UNIQUE (animal_ativo),
  CONSTRAINT uk_um_vinculo_ativo_por_chip   UNIQUE (chip_ativo),
  CONSTRAINT fk_vinculo_animal FOREIGN KEY (id_animal)      REFERENCES animal (id_animal),
  CONSTRAINT fk_vinculo_vet    FOREIGN KEY (id_veterinario) REFERENCES veterinario (id_veterinario)
) ENGINE=InnoDB;

-- ---------------- INTEGRAÇÃO GOVERNAMENTAL ----------------
-- Acompanha, no banco da clínica, as operações enviadas à API governamental simulada
-- (que tem banco próprio).

CREATE TABLE IF NOT EXISTS integracao_governo (
  id_integracao       INT AUTO_INCREMENT PRIMARY KEY,
  id_animal           INT          NOT NULL,
  id_vacina           INT          NULL,   -- só preenchido em operações de vacina
  tipo_operacao       ENUM('CADASTRO_ANIMAL','ATUALIZACAO_ANIMAL','VACINA_ANTIRRABICA') NOT NULL,
  status              ENUM('PENDENTE','ENVIADO','CONFIRMADO','FALHA') NOT NULL DEFAULT 'PENDENTE',
  chave_idempotencia  VARCHAR(100) NOT NULL,
  protocolo           VARCHAR(60)  NULL,
  tentativas          INT          NOT NULL DEFAULT 0,
  data_criacao        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultima_tentativa    DATETIME     NULL,
  data_confirmacao    DATETIME     NULL,
  mensagem_erro       VARCHAR(500) NULL,
  CONSTRAINT uk_integracao_idempotencia UNIQUE (chave_idempotencia),
  CONSTRAINT fk_integracao_animal FOREIGN KEY (id_animal) REFERENCES animal (id_animal),
  CONSTRAINT fk_integracao_vacina FOREIGN KEY (id_vacina) REFERENCES vacina (id_vacina)
) ENGINE=InnoDB;
