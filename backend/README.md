# ServiciosBogotá — Backend

API REST con FastAPI + SQLAlchemy. La guía de instalación y las variables de entorno están en el [README principal](../README.md).

- Documentación interactiva: `/docs` (Swagger) y `/redoc`
- Salud: `/health`

## Estructura

```
app/
├── api/v1/endpoints/   # Rutas HTTP (auth, businesses, reviews, contacts, payments, admin)
├── core/               # Configuración, JWT, dependencias, límite de peticiones
├── db/                 # Conexión y datos semilla (categorías, admin inicial)
├── models/             # Tablas SQLAlchemy
├── schemas/            # Validación Pydantic
└── services/           # Lógica de negocio (negocios, suscripciones, Wompi, imágenes)
tests/                  # Pruebas de API con pytest
```

## Convenciones

- Las rutas de colección se declaran con `""` (sin barra final) para evitar redirecciones 307, que detrás del proxy de Railway terminaban en `http://` y el navegador las bloqueaba.
- Los endpoints públicos de escritura (login, registro, reseñas, contacto) tienen límite de peticiones por IP.
- La activación de planes es idempotente por id de transacción de Wompi.
