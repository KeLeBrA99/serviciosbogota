# ServiciosBogotá — Backend

API REST con FastAPI + MySQL para el directorio de servicios locales.

## Setup local

```bash
# 1. Clonar e ir a la carpeta
cd backend

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus credenciales de MySQL

# 5. Inicializar base de datos (crea tablas + datos semilla)
python -m app.db.init_db

# 6. Correr servidor de desarrollo
uvicorn main:app --reload --port 8000
```

## Documentación API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estructura

```
app/
├── api/v1/endpoints/   # Rutas HTTP
├── core/               # Config, JWT, dependencias
├── db/                 # Conexión y seed
├── models/             # Tablas SQLAlchemy
├── schemas/            # Validación Pydantic
└── services/           # Lógica de negocio
```

## Variables de entorno necesarias

Ver `.env.example` para la lista completa.

## Deploy en Railway

1. Conectar repositorio GitHub a Railway
2. Añadir las variables de entorno del `.env.example`
3. Railway detecta automáticamente FastAPI y despliega
4. Añadir plugin MySQL en Railway y copiar `DATABASE_URL`
