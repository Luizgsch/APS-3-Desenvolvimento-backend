from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from database import criar_tabelas, engine
from controller.evento_controller import router as evento_router
from controller.participante_controller import router as participante_router
from controller.inscricao_controller import router as inscricao_router
from controller.relatorio_controller import router as relatorio_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        criar_tabelas()
        yield
    finally:
        engine.dispose()


app = FastAPI(title="API de Eventos Acadêmicos", description="API para gerenciamento de eventos, participantes e inscrições.", version="1.0.0", lifespan=lifespan)
app.include_router(evento_router)
app.include_router(participante_router)
app.include_router(inscricao_router)
app.include_router(relatorio_router)


@app.exception_handler(SQLAlchemyError)
async def tratar_erro_persistencia(request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Não foi possível acessar os dados. Tente novamente."},
    )

@app.get("/")
def inicio():
    return {"mensagem": "API de Eventos Acadêmicos funcionando."}
