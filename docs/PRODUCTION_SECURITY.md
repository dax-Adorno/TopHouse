# Seguridad de producción

La API falla al iniciar si `APP_ENV=production` conserva una configuración
insegura. Antes de desplegar se deben definir, como mínimo:

```dotenv
APP_ENV=production
DEBUG=false
SESSION_COOKIE_SECURE=true
CORS_ORIGINS=https://www.tophouse.com
ALLOWED_HOSTS=api.tophouse.com
```

`CORS_ORIGINS` acepta una lista separada por comas y en producción solo admite
orígenes HTTPS. `ALLOWED_HOSTS` contiene nombres de host sin esquema ni ruta y
no admite el comodín `*` en producción.

## Controles de la aplicación

- Cookies de sesión `Secure`, `HttpOnly`, `SameSite=Lax` y protección CSRF.
- Validación del encabezado `Host` para reducir ataques de host-header.
- Métodos y encabezados CORS limitados a los usados por la aplicación.
- Swagger, ReDoc y el esquema OpenAPI deshabilitados en producción.
- HSTS, CSP, anti-framing, `nosniff`, política de referente y permisos mínimos.

## Responsabilidad del proxy

El balanceador o reverse proxy debe terminar HTTPS, redirigir HTTP a HTTPS,
preservar el host original y limitar el tamaño máximo de requests. HSTS solo se
emite en producción; no debe habilitarse antes de comprobar HTTPS en todos los
subdominios incluidos.
