"""Endpoints de registro e inicio de sesión."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.dependencias import SesionDB
from app.esquemas.usuario import TokenRespuesta, UsuarioCrear, UsuarioLogin, UsuarioRespuesta
from app.modelos.usuario import Usuario
from app.nucleo.seguridad import crear_token_acceso, hashear_contrasena, verificar_contrasena

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def registrar_usuario(datos: UsuarioCrear, db: SesionDB) -> Usuario:
    """Registra un usuario siempre que su nombre no esté ocupado."""

    usuario_existente = db.scalar(select(Usuario).where(Usuario.username == datos.username))
    if usuario_existente is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El nombre de usuario ya está registrado.")

    usuario = Usuario(username=datos.username, password_hash=hashear_contrasena(datos.password))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenRespuesta)
def iniciar_sesion(credenciales: UsuarioLogin, db: SesionDB) -> TokenRespuesta:
    """Valida credenciales y entrega un token de acceso Bearer."""

    usuario = db.scalar(select(Usuario).where(Usuario.username == credenciales.username))
    if usuario is None or not verificar_contrasena(credenciales.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenRespuesta(access_token=crear_token_acceso({"sub": str(usuario.id)}))
