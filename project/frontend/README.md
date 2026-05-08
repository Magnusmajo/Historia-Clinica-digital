# Frontend

Interfaz React/Vite para Historia Clinica Digital.

## Variables

```env
VITE_API_URL
VITE_CSRF_COOKIE_NAME
```

`VITE_API_URL` usa `/api` por defecto. En desarrollo, Vite proxyea `/api` al backend local en `http://127.0.0.1:8001`; en Docker, Nginx proxyea `/api` al servicio backend. La sesion usa cookies HttpOnly emitidas por el backend; el frontend solo envia credenciales y el token CSRF.

## Ejecutar

```powershell
npm install
npm run dev
```

## Checks

```powershell
npm run lint
npm run build
```
