
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE IF NOT EXISTS denuncias (
    id_denuncia INT PRIMARY KEY AUTO_INCREMENT,
    tipo_chave_pix VARCHAR(255),
    nome_conta VARCHAR(255),
    cpf_cnpj VARCHAR(255),
    agencia VARCHAR(255),
    conta VARCHAR(255),
    banco VARCHAR(255),
    numero_bo VARCHAR(255),
    anexo LONGBLOB,
    descricao VARCHAR(255),
    data_denuncia VARCHAR(255)
);

SET FOREIGN_KEY_CHECKS=1;
