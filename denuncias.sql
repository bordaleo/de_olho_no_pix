CREATE DATABASE IF NOT EXISTS meu_banco;
USE meu_banco;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE IF NOT EXISTS denuncias (
    id_denuncia INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Campos Obrigatórios
    tipo_chave_pix VARCHAR(15) NOT NULL,
    chave_pix VARCHAR(100) NOT NULL,
    nome_conta VARCHAR(100) NOT NULL,
    cpf_cnpj VARCHAR(14) NOT NULL,
    banco VARCHAR(100) NOT NULL,
    numero_bo VARCHAR(50) NOT NULL,
    anexo LONGBLOB NOT NULL,
    
    -- Campos Opcionais
    agencia VARCHAR(10) NULL,
    conta VARCHAR(20) NULL,
    descricao VARCHAR(500) NULL,
    
    -- Campos Gerenciados pelo Sistema
    grupo_fraude_id VARCHAR(255) NULL,
    data_denuncia DATETIME DEFAULT CURRENT_TIMESTAMP, -- CORREÇÃO (era VARCHAR(10))

    -- Índices para performance
    INDEX idx_chave_pix (chave_pix),
    INDEX idx_grupo_fraude (grupo_fraude_id)
);

SET FOREIGN_KEY_CHECKS=1;