import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus  # <-- NOVO IMPORT para senhas

# Carrega o .env
load_dotenv()

# 1. Pega as variáveis (com valores padrão para segurança)
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "de_olho_no_pix")

# 2. CODIFICA A SENHA para que caracteres especiais (como @, :, /)
#    não quebrem a URL.
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)

# 3. Constrói a URL de forma segura
#    Isso evita o problema ':@' se o usuário ou senha estiverem vazios.
if DB_USER and ENCODED_PASSWORD:
    auth_part = f"{DB_USER}:{ENCODED_PASSWORD}@"
elif DB_USER:
    auth_part = f"{DB_USER}@"
else:
    auth_part = ""  # Sem usuário, sem senha

DATABASE_URL = f"mysql+asyncmy://{auth_part}{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 3. O resto do seu arquivo continua exatamente igual
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()