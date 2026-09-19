# Plataforma de películas

Aplicación web para buscar películas mediante TMDb y guardar una lista personal de favoritas.

## Cómo correr el proyecto localmente

### 1. Backend

Requisitos: Python 3.12+, PostgreSQL y un token de lectura de TMDb.

1. Crear una base de datos y cargar el esquema:

   ```bash
   createdb peliculas
   psql -d peliculas -f backend/schema.sql

2. Crear y activar un entorno virtual:
   
  cd backend
  python -m venv .venv
  source .venv/bin/activate
  
3. Instalar dependencias:

  pip install -r requirements.txt
   
4. Crear un archivo backend/.env tomando como referencia .env.example:

  DATABASE_URL=postgresql+psycopg2://usuario:password@localhost:5432/peliculas
  JWT_SECRET=un-secreto-de-al-menos-32-caracteres
  TMDB_API_TOKEN=tu-token-de-tmdb
  TMDB_LANGUAGE=es-ES
   
5. Iniciar la API:

uvicorn app.main:app --reload

### 2. Frontend  

1. En otra terminal, instalar dependencias:

  cd frontend
  npm ci

2. Iniciar el proyecto:
   
   npm run dev
   
3. Abrir Localhost

## Tecnologías usadas  

React + Vite: para construir una interfaz rápida y basada en componentes.

FastAPI: para crear una API con validación de datos y documentación automática.

PostgreSQL + SQLAlchemy: para almacenar usuarios y películas favoritas de forma persistente.

JWT y bcrypt: para autenticación y almacenamiento seguro de contraseñas.

TMDb: como fuente externa de información sobre películas.

Docker Compose: para levantar frontend, backend y base de datos en un mismo entorno.

## Decisiones técnicas

El token de TMDb se utiliza solo desde el backend para no exponerlo en el navegador.

Los favoritos se asocian al usuario autenticado; un usuario no puede modificar los favoritos de otro.

Se agregó una restricción para evitar guardar la misma película dos veces en favoritos.

Se validan los datos principales tanto en frontend como en backend.

Se manejan errores cuando TMDb no está disponible o no fue configurado.

Se dejaron tests para la integración con TMDb y para evitar duplicados en favoritos.

## Pendiente

Agregar paginación o botón de “cargar más” en las búsquedas.

Implementar caché de búsquedas y mejor manejo de límites de TMDb.

Añadir pruebas de integración completas y pruebas del frontend.

Mejorar la gestión de secretos y tokens para un entorno de producción.
