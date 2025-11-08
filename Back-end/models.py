from sqlalchemy import Column, Integer, String, DateTime, func, LargeBinary
from database import Base
# Este 'Base' é o que estava com a linha amarela. 
# Agora que o estamos usando aqui, o aviso sumirá de lá.

class Usuario(Base):
    """
    Modelo Python que espelha a tabela 'usuarios' do banco de dados.
    """
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    cpf = Column(String(11), unique=True, nullable=False, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    data_criacao = Column(DateTime, server_default=func.now())
    telefone = Column(String(11), nullable=True)


class Denuncia(Base):
    """
    Modelo Python que espelha a tabela 'denuncias' do banco de dados.
    """
    __tablename__ = "denuncias"

    id_denuncia = Column(Integer, primary_key=True, index=True)
    
    grupo_fraude_id = Column(String(255), nullable=True, index=True)

    # --- Campos Obrigatórios (baseado no HTML) ---
    tipo_chave_pix = Column(String(15), nullable=False)
    nome_conta = Column(String(100), nullable=False)
    chave_pix = Column(String(100), nullable=False, index=True)
    numero_bo = Column(String(50), nullable=False)
    banco = Column(String(100), nullable=False) 
    cpf_cnpj = Column(String(14), nullable=False) 
    
    # O tipo 'LargeBinary' é como o SQLAlchemy entende o 'LONGBLOB'
    anexo = Column(LargeBinary(length=(2**32)-1), nullable=False)

    agencia = Column(String(10), nullable=True)
    conta = Column(String(20), nullable=True)
    descricao = Column(String(255), nullable=True)

    # --- Campo Automático ---
    data_denuncia = Column(DateTime, server_default=func.now())