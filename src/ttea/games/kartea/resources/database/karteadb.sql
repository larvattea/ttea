-- -----------------------------------------------------
-- KarTEA - esquema do banco de dados (MySQL 8)
--
-- Atualizado em 2026-10-09 para refletir os modelos Python e os CSVs
-- gravados pelo jogo (pasta players/). Gerado originalmente pelo MySQL
-- Workbench em 2026-01-20; o modelo karteamodel.mwb e o diagrama
-- karteacsv.png NÃO foram atualizados junto.
--
-- Convenções:
-- - Datas em ISO 8601 (DATE, 'YYYY-MM-DD') e horas locais (TIME,
--   'HH:MM:SS'); o fuso da sessão fica em utc_offset ('-03:00').
-- - IDs vêm dos CSVs (sem AUTO_INCREMENT), para manter as referências.
-- - Booleanos são TINYINT(1); nos CSVs aparecem como True/False.
--
-- Mapeamento CSV -> tabela (colunas com nome diferente):
--   *_kartea_session.csv         player -> player_id,
--                                professional -> professional_id
--   *_kartea_session_detail.csv  session -> player_kartea_session_id
--   *_kartea_config.csv          player -> player_id,
--                                session -> player_kartea_session_id,
--                                phase -> kartea_phase_id,
--                                level -> kartea_phase_level_id
-- -----------------------------------------------------

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema karteadb
-- utf8mb4: suporta qualquer caractere (nomes com acento, trema etc.)
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `karteadb` ;

CREATE SCHEMA IF NOT EXISTS `karteadb`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci ;
USE `karteadb` ;

-- -----------------------------------------------------
-- Table `karteadb`.`player`
-- Cadastro da plataforma T-TEA (ttea.model.Player).
-- -----------------------------------------------------
DROP TABLE IF EXISTS `karteadb`.`player` ;

CREATE TABLE IF NOT EXISTS `karteadb`.`player` (
  `id` INT NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `birth_date` DATE NOT NULL,
  `observation` TEXT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `karteadb`.`professional`
-- Cadastro da plataforma T-TEA (ttea.model.Professional).
-- Estrutura mínima: completar com os demais campos do modelo.
-- -----------------------------------------------------
DROP TABLE IF EXISTS `karteadb`.`professional` ;

CREATE TABLE IF NOT EXISTS `karteadb`.`professional` (
  `id` INT NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `karteadb`.`kartea_phase`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `karteadb`.`kartea_phase` ;

CREATE TABLE IF NOT EXISTS `karteadb`.`kartea_phase` (
  `id` INT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `karteadb`.`kartea_phase_level`
-- Origem: resources/phases/{fase}.csv
-- interval: segundos entre objetos (aceita frações, ex.: 7.5)
-- obj_type: lista JSON com o tipo de cada objeto (0 alvo, 1 obstáculo)
-- -----------------------------------------------------
DROP TABLE IF EXISTS `karteadb`.`kartea_phase_level` ;

CREATE TABLE IF NOT EXISTS `karteadb`.`kartea_phase_level` (
  `kartea_phase_id` INT NOT NULL,
  `id` INT NOT NULL,
  `interval` DECIMAL(5,2) NOT NULL,
  `num_obj` INT NOT NULL,
  `obj_type` JSON NOT NULL,
  PRIMARY KEY (`kartea_phase_id`, `id`),
  INDEX `fk_kartea_phase_level_kartea_phase1_idx` (`kartea_phase_id` ASC) VISIBLE,
  CONSTRAINT `fk_kartea_phase_level_kartea_phase1`
    FOREIGN KEY (`kartea_phase_id`)
    REFERENCES `karteadb`.`kartea_phase` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `karteadb`.`kartea_event_type`
-- Tipos de evento do detalhe da sessão
-- (PlayerKarteaSessionDetail.EventType). `name` é o texto gravado no
-- CSV, sempre em português; a tradução é feita só na exibição.
-- Comparação exata (acentos e maiúsculas): utf8mb4_0900_as_cs.
-- -----------------------------------------------------
DROP TABLE IF EXISTS `karteadb`.`kartea_event_type` ;

CREATE TABLE IF NOT EXISTS `karteadb`.`kartea_event_type` (
  `name` VARCHAR(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL,
  `code` VARCHAR(64) NOT NULL,
  `category` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`name`),
  UNIQUE INDEX `code_UNIQUE` (`code` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `karteadb`.`player_kartea_session`
-- Uma linha por execução do jogo. Totais acumulados de todos os níveis
-- jogados (inclusive o interrompido); phase_reached/level_reached é a
-- fase/nível atual (último) da sessão, igual ao player_kartea_config e
-- ao último evento do detalhe (acompanha também os retrocessos).
-- -----------------------------------------------------
DROP TABLE IF EXISTS `karteadb`.`player_kartea_session` ;

CREATE TABLE IF NOT EXISTS `karteadb`.`player_kartea_session` (
  `id` INT NOT NULL,
  `player_id` INT NOT NULL,
  `professional_id` INT NOT NULL,
  `start_date` DATE NOT NULL,
  `start_time` TIME NOT NULL,
  `end_date` DATE NOT NULL,
  `end_time` TIME NOT NULL,
  `phase_reached` INT NOT NULL,
  `level_reached` INT NOT NULL,
  `general_score` INT NOT NULL DEFAULT 0,
  `q_movement` INT NOT NULL DEFAULT 0,
  `q_collided_target` INT NOT NULL DEFAULT 0,
  `q_avoided_target` INT NOT NULL DEFAULT 0,
  `q_collided_obstacle` INT NOT NULL DEFAULT 0,
  `q_avoided_obstacle` INT NOT NULL DEFAULT 0,
  `utc_offset` CHAR(6) NULL COMMENT 'Ex.: -03:00. NULL em sessões antigas (fuso desconhecido)',
  PRIMARY KEY (`id`),
  INDEX `fk_player_session_kartea_player_idx` (`player_id` ASC) VISIBLE,
  INDEX `fk_player_kartea_session_professional1_idx` (`professional_id` ASC) VISIBLE,
  CONSTRAINT `fk_player_session_kartea_player`
    FOREIGN KEY (`player_id`)
    REFERENCES `karteadb`.`player` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_player_kartea_session_professional1`
    FOREIGN KEY (`professional_id`)
    REFERENCES `karteadb`.`professional` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `karteadb`.`player_kartea_config`
-- Uma linha por jogador (configuração atual do jogo).
-- -----------------------------------------------------
DROP TABLE IF EXISTS `karteadb`.`player_kartea_config` ;

CREATE TABLE IF NOT EXISTS `karteadb`.`player_kartea_config` (
  `player_id` INT NOT NULL,
  `player_kartea_session_id` INT NULL,
  `update_session_id` TINYINT(1) NOT NULL,
  `kartea_phase_id` INT NOT NULL,
  `kartea_phase_level_id` INT NOT NULL,
  `level_time` INT NOT NULL,
  `vehicle_image` VARCHAR(255) NOT NULL,
  `horizon_image` VARCHAR(255) NOT NULL,
  `environment_image_right` VARCHAR(255) NOT NULL,
  `environment_image_left` VARCHAR(255) NOT NULL,
  `target_image` VARCHAR(255) NOT NULL,
  `obstacle_image` VARCHAR(255) NOT NULL,
  `positive_feedback_image` VARCHAR(255) NOT NULL,
  `neutral_feedback_image` VARCHAR(255) NOT NULL,
  `negative_feedback_image` VARCHAR(255) NOT NULL,
  `positive_feedback_sound` VARCHAR(255) NOT NULL,
  `neutral_feedback_sound` VARCHAR(255) NOT NULL,
  `negative_feedback_sound` VARCHAR(255) NOT NULL,
  `palette` INT NOT NULL,
  `hud` TINYINT(1) NOT NULL,
  `sound` TINYINT(1) NOT NULL,
  PRIMARY KEY (`player_id`),
  INDEX `fk_player_kartea_config_player_kartea_session1_idx` (`player_kartea_session_id` ASC) VISIBLE,
  INDEX `fk_player_kartea_config_kartea_phase_level1_idx` (`kartea_phase_id` ASC, `kartea_phase_level_id` ASC) VISIBLE,
  CONSTRAINT `fk_player_config_kartea_player1`
    FOREIGN KEY (`player_id`)
    REFERENCES `karteadb`.`player` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_player_kartea_config_player_kartea_session1`
    FOREIGN KEY (`player_kartea_session_id`)
    REFERENCES `karteadb`.`player_kartea_session` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_player_kartea_config_kartea_phase_level1`
    FOREIGN KEY (`kartea_phase_id` , `kartea_phase_level_id`)
    REFERENCES `karteadb`.`kartea_phase_level` (`kartea_phase_id` , `id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `karteadb`.`player_kartea_session_detail`
-- Uma linha por evento. event_date + event_time (hora local, no fuso
-- utc_offset da sessão). Para ordenar eventos, use `id` (sequencial).
-- CSVs gravados antes de 2026-10-09 têm a coluna "date_time" no lugar de
-- "event_date": rode util/migratecsvisodates.py antes de importar.
-- -----------------------------------------------------
DROP TABLE IF EXISTS `karteadb`.`player_kartea_session_detail` ;

CREATE TABLE IF NOT EXISTS `karteadb`.`player_kartea_session_detail` (
  `id` INT NOT NULL,
  `player_kartea_session_id` INT NOT NULL,
  `event_date` DATE NOT NULL,
  `event_time` TIME NOT NULL,
  `phase` INT NOT NULL,
  `level` INT NOT NULL,
  `player_position` INT NOT NULL COMMENT '0 esquerda, 1 meio, 2 direita, -1 fora da área',
  `event_position` INT NOT NULL,
  `event_type` VARCHAR(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_player_kartea_session_detail_player_kartea_session1_idx` (`player_kartea_session_id` ASC) VISIBLE,
  INDEX `fk_player_kartea_session_detail_kartea_event_type1_idx` (`event_type` ASC) VISIBLE,
  CONSTRAINT `fk_player_kartea_session_detail_player_kartea_session1`
    FOREIGN KEY (`player_kartea_session_id`)
    REFERENCES `karteadb`.`player_kartea_session` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_player_kartea_session_detail_kartea_event_type1`
    FOREIGN KEY (`event_type`)
    REFERENCES `karteadb`.`kartea_event_type` (`name`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Dados de referência
-- -----------------------------------------------------
INSERT INTO `karteadb`.`kartea_phase` (`id`) VALUES (1), (2), (3);

-- Origem: resources/phases/1.csv, 2.csv e 3.csv
INSERT INTO `karteadb`.`kartea_phase_level`
  (`kartea_phase_id`, `id`, `interval`, `num_obj`, `obj_type`) VALUES
  (1, 1, 10, 12, '[0,0,0,0,0,0,0,0,0,0,0,0]'),
  (1, 2, 10, 12, '[0,0,0,0,0,0,0,0,0,0,0,0]'),
  (1, 3, 7.5, 16, '[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]'),
  (1, 4, 7.5, 16, '[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]'),
  (1, 5, 5, 24, '[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]'),
  (1, 6, 5, 24, '[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]'),
  (1, 7, 3, 40, '[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]'),
  (2, 1, 10, 12, '[1,1,1,1,1,1,1,1,1,1,1,1]'),
  (2, 2, 10, 12, '[1,1,1,1,1,1,1,1,1,1,1,1]'),
  (2, 3, 7.5, 16, '[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]'),
  (2, 4, 7.5, 16, '[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]'),
  (2, 5, 5, 24, '[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]'),
  (2, 6, 5, 24, '[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]'),
  (2, 7, 3, 40, '[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]'),
  (3, 1, 10, 12, '[0,1,0,1,0,1,0,1,0,1,0,1]'),
  (3, 2, 10, 12, '[0,1,0,1,0,1,0,1,0,1,0,1]'),
  (3, 3, 7.5, 16, '[0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]'),
  (3, 4, 7.5, 16, '[0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]'),
  (3, 5, 5, 24, '[0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]'),
  (3, 6, 5, 24, '[0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]'),
  (3, 7, 3, 40, '[0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]');

-- Origem: model/playerkarteasessiondetail.py (EventType)
INSERT INTO `karteadb`.`kartea_event_type` (`name`, `code`, `category`) VALUES
  ('Colidiu com Alvo', 'COLLIDED_TARGET', 'Objeto'),
  ('Colidiu com Obstáculo', 'COLLIDED_OBSTACLE', 'Objeto'),
  ('Desviou de Alvo', 'AVOIDED_TARGET', 'Objeto'),
  ('Desviou de Obstáculo', 'AVOIDED_OBSTACLE', 'Objeto'),
  ('Criou Alvo', 'CREATED_TARGET', 'Objeto'),
  ('Criou Obstáculo', 'CREATED_OBSTACLE', 'Objeto'),
  ('Trocou de Pista', 'CHANGED_LANE', 'Movimento'),
  ('Saiu da área do jogo', 'LEFT_GAME_AREA', 'Movimento'),
  ('Controle Jogo: Avanca Nível', 'GAME_CONTROL_ADVANCE_LEVEL', 'Recomendação do jogo'),
  ('Controle Jogo: Permanece Nível', 'GAME_CONTROL_MAINTAIN_LEVEL', 'Recomendação do jogo'),
  ('Controle Jogo: Retrocede Nível', 'GAME_CONTROL_REGRESS_LEVEL', 'Recomendação do jogo'),
  ('Controle UFE: Habilita HUD', 'UFE_CONTROL_ENABLE_HUD', 'Ação do profissional'),
  ('Controle UFE: Desabilita HUD', 'UFE_CONTROL_DISABLE_HUD', 'Ação do profissional'),
  ('Controle UFE: Habilita Som', 'UFE_CONTROL_ENABLE_SOUND', 'Ação do profissional'),
  ('Controle UFE: Desabilita Som', 'UFE_CONTROL_DISABLE_SOUND', 'Ação do profissional'),
  ('Controle UFE: Pause', 'UFE_CONTROL_PAUSE', 'Ação do profissional'),
  ('Controle UFE: Unpause', 'UFE_CONTROL_UNPAUSE', 'Ação do profissional'),
  ('Controle UFE: Avança Nível', 'UFE_CONTROL_ADVANCE_LEVEL', 'Ação do profissional'),
  ('Controle UFE: Reinicia Nível', 'UFE_CONTROL_RESTART_LEVEL', 'Ação do profissional'),
  ('Controle UFE: Retrocede Nível', 'UFE_CONTROL_REGRESS_LEVEL', 'Ação do profissional'),
  ('Controle UFE: Sai do Jogo', 'UFE_CONTROL_EXIT_GAME', 'Ação do profissional');


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
