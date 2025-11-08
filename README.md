
🔧 Guia de Instalação e Execução
Siga estes 3 passos para rodar o projeto.

1. Configuração do Banco de Dados (MySQL)
O backend precisa de um banco de dados para armazenar os usuários e as denúncias.

Inicie seu servidor MySQL.

Abra seu gerenciador de banco de dados (HeidiSQL, DBeaver, etc.) e rode os scripts SQL (que estão na raiz do projeto) na seguinte ordem:

SQL

-- 1. Crie o banco de dados (use este nome ou mude no .env)
CREATE DATABASE IF NOT EXISTS meu_banco;
USE meu_banco;

-- 2. Rode o conteúdo do arquivo 'usuarios.sql' para criar a tabela de usuários.

-- 3. Rode o conteúdo do arquivo 'denuncias.sql' para criar a tabela de denúncias.

-- 4. ATENÇÃO: Rode este comando para adicionar a coluna de agrupamento
ALTER TABLE denuncias 
ADD COLUMN grupo_fraude_id VARCHAR(255) NULL,
ADD INDEX idx_grupo_fraude (grupo_fraude_id);

1. Configuração do Backend (Python)
O backend é o servidor FastAPI que vai processar os dados.

Navegue até a pasta Back-end do projeto.

Crie um ambiente virtual (venv):

Bash

python -m venv venv
Ative o ambiente virtual:

No Windows (CMD/PowerShell):

Bash

.\venv\Scripts\activate
No macOS/Linux:

Bash

source venv/bin/activate
Com o venv ativo, instale todas as dependências do projeto:

    pip install -r requirements.txt
    Crie o arquivo de configuração:

Na pasta Back-end, copie o arquivo .env.example e renomeie a cópia para .env.

Abra o novo arquivo .env e preencha as credenciais do seu banco de dados (que você configurou no Passo 1).

# .env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha_do_mysql  # <--- COLOQUE SUA SENHA AQUI
DB_NAME=meu_banco            # <--- Deve ser o mesmo nome do SQL
SECRET_KEY=qualquer_coisa_secreta_e_longa_12345
3. Configuração do Frontend (HTML)
O frontend é um arquivo HTML simples e não precisa de instalação.

Nenhuma ação é necessária.

O arquivo olhonopix.html já está configurado para fazer chamadas à API no http://localhost:8000.