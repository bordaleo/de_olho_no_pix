from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ==================================
#         SCHEMAS DE USUÁRIO
# ==================================

class UsuarioBase(BaseModel):
    """
    Campos comuns que um usuário tem.
    """
    email: EmailStr  # Valida o formato do e-mail automaticamente
    nome: str
    cpf: str
    telefone: Optional[str] = None # 'Optional' significa que pode ser None


class UsuarioCreate(UsuarioBase):
    """
    Schema para ENTRADA (criação de usuário).
    Recebe os campos comuns + a senha em texto puro.
    """
    senha: str  # Recebemos a senha, vamos criptografar antes de salvar


class Usuario(UsuarioBase):
    """
    Schema para SAÍDA (leitura de usuário).
    Mostra os campos comuns + os gerados pelo banco.
    IMPORTANTE: Não tem o campo 'senha' nem 'senha_hash'.
    """
    id_usuario: int
    data_criacao: datetime

    class Config:
        # Permite que o Pydantic leia dados de um objeto SQLAlchemy
        from_attributes = True 

class UsuarioUpdate(BaseModel):
    """
    Schema para ATUALIZAÇÃO de usuário.
    Todos os campos são opcionais.
    """
    nome: Optional[str] = None  # <-- ADICIONADO
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    senha: Optional[str] = None


# ==================================
#         SCHEMAS DE LOGIN
# ==================================

class LoginRequest(BaseModel):
    """
    Schema para ENTRADA (tentativa de login).
    """
    email: EmailStr
    senha: str


class Token(BaseModel):
    """
    Schema para SAÍDA (sucesso no login).
    """
    access_token: str
    token_type: str


# ==================================
#         SCHEMAS DE DENÚNCIA
# ==================================
class Denuncia(BaseModel):
    """
    Schema para SAÍDA (leitura de UMA denúncia).
    Usado como resposta ao criar uma nova denúncia.
    """
    id_denuncia: int
    tipo_chave_pix: str
    chave_pix: str
    nome_conta: str
    numero_bo: str
    data_denuncia: datetime

    # Campos que agora são obrigatórios
    cpf_cnpj: str
    banco: str

    # Campos opcionais
    agencia: Optional[str] = None
    conta: Optional[str] = None
    descricao: Optional[str] = None

    # Não incluímos o 'anexo' (BLOB)

    class Config:
        from_attributes = True

class ResetRequest(BaseModel):
    """Schema para receber o pedido de troca de senha final."""
    token: str
    new_password: str

class DenunciaAgrupada(BaseModel):
    """
    Schema para SAÍDA (Pesquisa).
    Mostra os dados agrupados por fraude.
    """
    # Campos do grupo
    nome_conta: str
    cpf_cnpj: str
    banco: str

    # Um exemplo de chave pix usada nesse grupo
    chave_pix_exemplo: str 

    # A contagem total
    total_denuncias: int

    class Config:
        from_attributes = True