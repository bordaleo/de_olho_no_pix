import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, or_, func, tuple_
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

async def get_denuncias_by_query(db: AsyncSession, query: str | None) -> list[tuple]:
    """
    Busca denúncias AGRUPADAS por grupo_fraude_id.
    Retorna uma lista de tuplas com os dados do grupo e a contagem.
    """

    # Seleciona os campos que queremos agrupar e contar
    statement = select(
        models.Denuncia.nome_conta,
        models.Denuncia.cpf_cnpj,
        models.Denuncia.banco,
        func.max(models.Denuncia.chave_pix).label("chave_pix_exemplo"), # Pega uma chave de exemplo
        func.count(models.Denuncia.id_denuncia).label("total_denuncias") # Conta as denúncias
    ).group_by(
        models.Denuncia.grupo_fraude_id,
        models.Denuncia.nome_conta,
        models.Denuncia.cpf_cnpj,
        models.Denuncia.banco
    ).order_by(
        func.count(models.Denuncia.id_denuncia).desc() # Ordena pelos mais denunciados
    )

    # Se o usuário digitou algo na busca...
    if query:
        like_query = f"%{query}%"
        # Adiciona o filtro (WHERE)
        statement = statement.filter(
            or_(
                models.Denuncia.chave_pix.like(like_query),
                models.Denuncia.nome_conta.like(like_query),
                models.Denuncia.banco.like(like_query),
                models.Denuncia.cpf_cnpj.like(like_query)
            )
        )

    result = await db.execute(statement)
    return result.all()  # Retorna uma lista de resultados (tuplas)

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