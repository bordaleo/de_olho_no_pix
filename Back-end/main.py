import os
import bcrypt
import auth
from datetime import datetime, timedelta
from typing import List, Annotated

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

# Importando todos os nossos módulos locais
import crud, models, schemas
from database import get_db, engine, Base
from dotenv import load_dotenv
# ==================================
#         CONFIGURAÇÃO DE AUTH (JWT)
# ==================================
# Vamos ler os segredos do nosso arquivo .env
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ==================================
#         CRIAÇÃO DO APP
# ==================================

# 1. Cria a instância principal do FastAPI
app = FastAPI(title="De Olho no Pix API")


# 2. Configura o CORS (Cross-Origin Resource Sharing)
# Isso é OBRIGATÓRIO para permitir que seu
# olhonopix.html (rodando em file:// ou localhost:xxxx)
# possa "chamar" sua API (rodando em localhost:8000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (para testes)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)


# ==================================
#         EVENTO DE STARTUP
# ==================================

@app.on_event("startup")
async def on_startup():
    """
    Função executada quando a API inicia.
    Isso garante que todas as tabelas (definidas em models.py)
    sejam criadas no banco de dados.
    """
    async with engine.begin() as conn:
        # Cria as tabelas
        await conn.run_sync(Base.metadata.create_all)


# ==================================
#         FUNÇÕES DE AUTH
# ==================================
# (Estas são as rotas e funções para o seu usuarios.sql)

def create_access_token(data: dict):
    """Cria um token JWT para o login."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/api/register", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UsuarioCreate, db: AsyncSession = Depends(get_db)):
    """
    Rota para o formulário de '#cadastro'
    """
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    
    return await crud.create_user(db=db, user=user)


@app.post("/api/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: schemas.LoginRequest, db: AsyncSession = Depends(get_db)
):
    """
    Rota para o formulário de '#inicio' (login)
    """
    user = await crud.get_user_by_email(db, email=form_data.email)
    
    # Verifica se o usuário existe e se a senha está correta
    if not user or not crud.verify_password(form_data.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria o token de acesso
    access_token = create_access_token(
        data={"sub": user.email, "id": user.id_usuario}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ==================================
#       ROTAS DE DENÚNCIA
# ==================================
# (Estas são as rotas para o seu olhonopix.html)

@app.post("/api/denuncias", response_model=schemas.Denuncia, status_code=status.HTTP_201_CREATED)
async def criar_denuncia(
    # --- CAMPOS OBRIGATÓRIOS VÊM PRIMEIRO ---
    anexo: Annotated[UploadFile, File()],
    tipo_chave_pix: Annotated[str, Form()],
    nome_conta: Annotated[str, Form()],
    chave_pix: Annotated[str, Form()],
    numero_bo: Annotated[str, Form()],
    cpf_cnpj: Annotated[str, Form()],
    banco: Annotated[str, Form()],

    # --- DEPENDÊNCIAS E OPCIONAIS ---
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_user), # <-- SEGURANÇA ADICIONADA

    # Opcionais
    agencia: Annotated[str | None, Form()] = None,
    conta: Annotated[str | None, Form()] = None,
    descricao: Annotated[str | None, Form()] = None,
    valor: Annotated[str | None, Form()] = None # <-- CAMPO DO AMIGO
):
    """
    Rota para o formulário de '#denunciar'.
    AGORA PROTEGIDA POR LOGIN.
    """
    anexo_bytes = await anexo.read()

    db_denuncia = await crud.create_denuncia(
        db=db,
        anexo_bytes=anexo_bytes,
        tipo_chave_pix=tipo_chave_pix,
        chave_pix=chave_pix,
        nome_conta=nome_conta,
        numero_bo=numero_bo,
        cpf_cnpj=cpf_cnpj,
        banco=banco,
        agencia=agencia,
        conta=conta,
        descricao=descricao
        # Nota: 'valor' não está no nosso model/crud, então é ignorado.
    )
    return db_denuncia


# Esta é a rota de BUSCA (GET)
@app.get("/api/denuncias", response_model=List[schemas.Denuncia])
async def pesquisar_denuncias(
    q: str | None = None,
    tipo: str | None = None, 
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_user)
):
    """
    Rota para a tela '#pesquisar' (MODO DETALHADO).
    AGORA PROTEGIDA POR LOGIN.
    """
    denuncias = await crud.get_denuncias_by_query(db, query=q, tipo=tipo)
    return denuncias


@app.get("/api/denuncias/{denuncia_id}/anexo")
async def baixar_anexo(denuncia_id: int, db: AsyncSession = Depends(get_db)):
    """
    Rota para baixar o B.O. (anexo) de uma denúncia específica.
    """
    anexo_bytes = await crud.get_denuncia_anexo_by_id(db, denuncia_id=denuncia_id)
    
    if not anexo_bytes:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")
    
    # Retorna o arquivo (LONGBLOB) diretamente como uma resposta.
    # O media_type="application/octet-stream" força o download.
    return Response(content=anexo_bytes, media_type="application/octet-stream")


@app.get("/")
def read_root():
    """Rota principal (teste)"""
    return {"status": "API 'De Olho no Pix' rodando!"}