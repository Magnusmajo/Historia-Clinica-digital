# Frontend

Interfaz React/Vite para Historia Clinica Digital.

## Variables

```env
VITE_API_URL
VITE_CSRF_COOKIE_NAME
```

`VITE_API_URL` apunta al backend directo en desarrollo y a `/api` cuando se sirve desde Nginx en Docker. La sesion usa cookies HttpOnly emitidas por el backend; el frontend solo envia credenciales y el token CSRF.

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
