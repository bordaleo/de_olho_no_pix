import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, or_, func
# Importamos os arquivos que já criamos
import models, schemas
# ==================================
#         FUNÇÕES DE SENHA
# ==================================

def hash_password(password: str) -> str:
    """Criptografa a senha em texto puro."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto puro bate com a senha criptografada."""
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


# ==================================
#         CRUD DE USUÁRIO
# ==================================

async def get_user_by_email(db: AsyncSession, email: str) -> models.Usuario | None:
    """Busca um usuário pelo seu e-mail."""
    statement = select(models.Usuario).filter(models.Usuario.email == email)
    result = await db.execute(statement)
    return result.scalars().first() # Retorna o usuário ou None


async def create_user(db: AsyncSession, user: schemas.UsuarioCreate) -> models.Usuario:
    """Cria um novo usuário no banco de dados."""
    
    # IMPORTANTE: Criptografa a senha antes de salvar
    hashed_password = hash_password(user.senha)
    
    db_user = models.Usuario(
        email=user.email,
        nome=user.nome,
        cpf=user.cpf,
        telefone=user.telefone,
        senha_hash=hashed_password  # Salva o HASH, nunca a senha pura
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# ==================================
#        CRUD DE DENÚNCIA
# ==================================

async def get_denuncias_by_query(
    db: AsyncSession, 
    query: str | None, 
    tipo: str | None  # <-- Novo parâmetro do amigo
) -> list[models.Denuncia]:
    """
    Busca denúncias na tela "Pesquisar" (MODO DETALHADO).
    """
    
    statement = select(models.Denuncia).order_by(models.Denuncia.data_denuncia.desc())

    # Filtro 1: Pelo termo de busca (query)
    if query:
        like_query = f"%{query}%"
        statement = statement.filter(
            or_(
                models.Denuncia.chave_pix.like(like_query),
                models.Denuncia.nome_conta.like(like_query),
                models.Denuncia.banco.like(like_query),
                models.Denuncia.numero_bo.like(like_query),
                models.Denuncia.cpf_cnpj.like(like_query)
            )
        )
    
    # Filtro 2: Pelo tipo de chave (do amigo)
    if tipo:
        statement = statement.filter(models.Denuncia.tipo_chave_pix == tipo)
    
    result = await db.execute(statement)
    return result.scalars().all()  # Retorna a lista detalhada

async def create_denuncia(
    db: AsyncSession, 
    anexo_bytes: bytes,
    tipo_chave_pix: str,
    chave_pix: str,
    nome_conta: str,
    numero_bo: str,
    cpf_cnpj: str, # MUDOU
    banco: str,   # MUDOU
    # Campos opcionais
    agencia: str | None,
    conta: str | None,
    descricao: str | None
) -> models.Denuncia:
    """
    Salva uma nova denúncia no banco, incluindo o arquivo B.O.
    """
    grupo_fraude_id = ""
    if tipo_chave_pix == "Chave aleatória":
        grupo_fraude_id = f"{nome_conta.lower().strip()}_{cpf_cnpj.strip()}"
    else:
        grupo_fraude_id = chave_pix.lower().strip()
    db_denuncia = models.Denuncia(
        anexo=anexo_bytes,
        tipo_chave_pix=tipo_chave_pix,
        chave_pix=chave_pix,
        nome_conta=nome_conta,
        numero_bo=numero_bo,
        cpf_cnpj=cpf_cnpj,
        banco=banco,
        agencia=agencia,
        conta=conta,
        descricao=descricao,
        grupo_fraude_id=grupo_fraude_id  # <-- ADICIONE ESTA LINHA
    )
    
    db.add(db_denuncia)
    await db.commit()
    await db.refresh(db_denuncia)
    return db_denuncia


async def get_denuncia_anexo_by_id(db: AsyncSession, denuncia_id: int) -> bytes | None:
    """
    Busca APENAS o arquivo (BLOB) de uma denúncia específica.
    """
    # Seleciona SÓ a coluna 'anexo' para ser rápido
    statement = select(models.Denuncia.anexo).filter(
        models.Denuncia.id_denuncia == denuncia_id
    )
    result = await db.execute(statement)
    return result.scalars().first() # Retorna os bytes do arquivo ou None