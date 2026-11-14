# ServiciosBogotá

Directorio de servicios locales para Bogotá: los vecinos buscan negocios por categoría y localidad, y los negocios reciben solicitudes, reseñas y pueden pagar un plan mensual para destacarse.

| Parte | Stack | Producción |
|-------|-------|------------|
| `backend/` | FastAPI · SQLAlchemy · MySQL | Railway — https://serviciosbogota-production.up.railway.app |
| `frontend/` | React 19 · Vite · Tailwind · Zustand | Vercel — https://serviciosbogota.vercel.app |

## Funcionalidades

- **Público:** búsqueda por texto, categoría y localidad (filtros en la URL), perfil del negocio con fotos, horario, WhatsApp, reseñas y formulario de contacto.
- **Dueños de negocio:** registro, crear/editar/eliminar negocios, logo y fotos (Cloudinary), horario de atención, bandeja de solicitudes, respuesta a reseñas, estadísticas básicas.
- **Planes:** Básico ($25.000/mes) y Premium ($65.000/mes) pagados con Wompi Web Checkout. El plan se activa por webhook y por verificación directa; vence solo a los 30 días.
- **Administración (`/admin`):** métricas, aprobar/suspender/destacar negocios, activar planes a mano (transferencia, Nequi), moderar reseñas, usuarios.

## Desarrollo local

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                               # completa DATABASE_URL y SECRET_KEY
uvicorn main:app --reload --port 8000              # crea tablas y categorías al arrancar

# Frontend (otra terminal)
cd frontend
npm install
cp .env.example .env
npm run dev                                        # http://localhost:5173
```

Para probar sin MySQL: `DATABASE_URL=sqlite:///./dev.db`.

Pruebas y verificación:

```bash
cd backend && pytest          # 16 pruebas de API (usa SQLite temporal)
cd frontend && npm run lint && npm run build
```

## Variables de entorno

**Backend (Railway)** — ver `backend/.env.example`.

| Variable | Para qué |
|----------|----------|
| `DATABASE_URL`, `SECRET_KEY` | Obligatorias |
| `FRONTEND_URL` | URL del frontend; Wompi redirige a `FRONTEND_URL/pago/confirmacion` |
| `CORS_ORIGINS` | Orígenes extra (el dominio de Vercel y localhost ya están incluidos) |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Crea el primer administrador al arrancar, si no existe |
| `WOMPI_PUBLIC_KEY`, `WOMPI_INTEGRITY_SECRET`, `WOMPI_EVENTS_SECRET`, `WOMPI_BASE_URL` | Pagos. En producción `WOMPI_BASE_URL=https://production.wompi.co/v1` |
| `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` | Subida de logo y fotos |

Sin las llaves de Wompi o Cloudinary la app funciona igual; esas funciones responden con un mensaje claro de "no configurado".

**Frontend (Vercel):** `VITE_API_URL` (ya definido en `frontend/.env.production`).

## Configurar Wompi

1. En el panel de Wompi → *Desarrolladores*, copia la llave pública, el secreto de **integridad** y el secreto de **eventos** a las variables de Railway.
2. En *URL de eventos* registra `https://<tu-backend>/api/v1/payments/wompi-webhook`.
3. Prueba primero con las llaves `pub_test_…` (sandbox) y una tarjeta de prueba.

## Notas

- Nunca subas archivos `.env` ni la carpeta `venv/`: ya están en `.gitignore`.
- Las tablas se crean con `create_all`, que **no** modifica tablas existentes. Si cambias un modelo, hay que migrar la base (Alembic ya está en las dependencias, pero aún sin configurar).
