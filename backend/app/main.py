"""Punto de entrada de la API FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import autenticacion_router, favoritos_router, peliculas_router

app = FastAPI(title="Plataforma de películas", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(autenticacion_router, prefix="/api/v1")
app.include_router(peliculas_router, prefix="/api/v1")
app.include_router(favoritos_router, prefix="/api/v1")


@app.get("/health", tags=["Salud"])
def estado_salud() -> dict[str, str]:
    """Endpoint liviano para comprobar que el servicio está disponible."""

    return {"status": "ok"}
