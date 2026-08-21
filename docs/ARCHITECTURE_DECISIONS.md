# Decisiones arquitectónicas de TopHouse

Actualizado: 21 de agosto de 2026.

Este archivo registra decisiones vigentes, no instrucciones inmutables. Una
decisión nueva que contradiga alguna de ellas debe explicarse en la
documentación y en el Pull Request que introduzca el cambio.

## Arquitectura y backend

- **FastAPI:** elección explícita para el backend del producto.
- **Monolito modular:** ofrece la mejor relación entre velocidad y
  mantenibilidad para un desarrollador principal. No se justifican
  microservicios en esta etapa.
- **PostgreSQL 17:** fuente de verdad relacional con constraints, índices y
  migraciones versionadas.
- **SQLAlchemy 2 + Alembic:** persistencia explícita y evolución controlada del
  esquema.
- **Dominio en español:** tabla `propiedades`, campos y valores del dominio se
  expresan en español.
- **Complejidad just-in-time:** Redis, workers, colas y bases vectoriales solo se
  incorporan ante una necesidad concreta.

## Calidad y entrega

- Black es el formatter oficial; Ruff realiza lint e imports.
- mypy se ejecuta en modo estricto.
- Las migraciones se revisan manualmente antes de aplicarse.
- CI prueba migraciones desde una base limpia mediante
  `upgrade -> downgrade base -> upgrade`.
- Todo cambio llega a `main` mediante Pull Request; se prefiere squash merge en
  PR pequeños y cohesivos.

## Ubicación y mapas

- PostgreSQL conserva `direccion`, `latitud` y `longitud` de forma neutral.
- No se almacena como fuente de verdad una URL o iframe de un proveedor.
- El proveedor se elige en frontend o configuración; OSM + Leaflet es la opción
  inicial sugerida para el MVP, no una dependencia del dominio.
- `mostrar_ubicacion_exacta` es `false` por defecto.
- Ocultar el marcador en UI no protege los datos: la API pública debe omitir o
  transformar coordenadas exactas cuando no estén autorizadas.
- Antes del endpoint público debe definirse si la dirección se omite, aproxima
  o muestra parcialmente.

## Autenticación y seguridad

- Autenticación administrativa con sesión/cookie segura; no persistir JWT en
  `localStorage`.
- Los roles iniciales son `administrador` y `operador`; todo usuario nuevo nace
  como `operador` y `activo=true` salvo decisión administrativa explícita.
- El email identifica de forma única a cada usuario.
- Autorización y RBAC se aplican en backend, no solo en la interfaz.
- Contraseñas con Argon2 y protección CSRF para operaciones autenticadas por
  cookie.
- El backend genera y verifica hashes Argon2 mediante `pwdlib`; nunca persiste
  ni devuelve contraseñas en texto plano.
- Los emails se normalizan a minúsculas antes de persistir o buscar, y un
  usuario inactivo no puede autenticarse.
- Las sesiones son opacas, expiran y pueden revocarse; PostgreSQL conserva solo
  hashes SHA-256 de tokens aleatorios de alta entropía, nunca los tokens que
  recibe el navegador.
- La cookie de sesión es `HttpOnly`, `Secure` y `SameSite=Lax`. El token CSRF
  separado debe enviarse en `X-CSRF-Token` para operaciones autenticadas que
  modifican estado.
- Rate limiting en superficies sensibles y controles contra IDOR, mass
  assignment, XSS e inyección.
- Acciones administrativas importantes deben producir audit log.
- `administrador` y `operador` pueden consultar, crear y editar propiedades;
  solo `administrador` puede cambiar su estado o condición de destacada.
- La auditoría conserva una copia del email del actor, acción, recurso,
  identificador y detalles del cambio aun si el usuario se elimina después.
- Secretos solo mediante variables de entorno; `.env` nunca se versiona.

## Contratos de API

- Los schemas Pydantic usarán `extra='forbid'` para rechazar campos no
  declarados.
- `slug`, identificadores y timestamps son controlados por backend.
- Crear una propiedad no permite establecer arbitrariamente `estado` o
  `destacada`; esos cambios pertenecen a flujos administrativos controlados.
- Deben existir respuestas públicas y administrativas separadas antes de
  exponer datos sensibles de ubicación.
- Los endpoints administrativos no se consideran aptos para producción hasta
  que estén protegidos por autenticación y RBAC en backend.

## Ciclo de vida de Propiedad

- `DELETE` aplica eliminación lógica: un administrador cambia el estado a
  `no_disponible`, quita `destacada` y genera auditoría. No se destruye el
  registro ni su historial.
- Los slugs se generan una sola vez al crear la propiedad y permanecen estables
  aunque cambie el título.
- Un slug duplicado recibe sufijos numéricos (`-2`, `-3`, etc.).
- `borrador` puede pasar a `publicada` o `no_disponible`.
- `publicada` puede pasar a `pausada`, `reservada`, `alquilada`, `vendida` o
  `no_disponible`.
- `pausada` puede volver a `publicada` o pasar a `no_disponible`.
- `reservada` puede volver a `publicada` o pasar a `alquilada`, `vendida` o
  `no_disponible`.
- `alquilada` puede volver a `publicada` al finalizar el contrato o pasar a
  `no_disponible`.
- `vendida` solo puede pasar a `no_disponible`.
- `no_disponible` puede reabrirse únicamente como `borrador`.

## Imágenes

- Producción utiliza object storage compatible con S3; no archivos locales
  persistentes.
- Cada propiedad admite hasta 20 imágenes; cada entrada acepta como máximo 10
  MB, dimensiones entre 320 y 12000 píxeles y contenido JPEG, PNG o WebP.
- PostgreSQL guarda metadatos y claves de objetos, no binarios. Garantiza orden
  único y una sola portada por propiedad.
- Los uploads se validan por contenido real, tamaño, dimensiones y formato.
- El pipeline normaliza orientación, elimina metadata innecesaria y genera WebP
  y thumbnails.
- El orden y la portada son gestionables desde administración.

## Inteligencia artificial

- El núcleo del MVP funciona sin IA ni costo obligatorio de proveedor.
- Futuras integraciones estarán aisladas detrás de una abstracción y feature
  flags.
- Acciones con impacto requieren revisión humana, salidas estructuradas,
  evaluaciones y defensas contra prompt injection.
