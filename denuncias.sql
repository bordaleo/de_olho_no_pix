CREATE DATABASE IF NOT EXISTS meu_banco;
USE meu_banco;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE IF NOT EXISTS denuncias (
    id_denuncia INT PRIMARY KEY AUTO_INCREMENT,
    tipo_chave_pix VARCHAR(15),
    chave_pix VARCHAR(100),
    nome_conta VARCHAR(100),
    cpf_cnpj VARCHAR(14),
    agencia VARCHAR(10),
    conta VARCHAR(20),
    banco VARCHAR(100),
    numero_bo VARCHAR(50),
    anexo LONGBLOB,
    descricao VARCHAR(255),
    data_denuncia VARCHAR(10),
    grupo_fraude_id VARCHAR(255) NULL
);

SET FOREIGN_KEY_CHECKS=1;