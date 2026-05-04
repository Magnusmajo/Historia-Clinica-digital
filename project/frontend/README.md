# Frontend

Interfaz React/Vite para Historia Clinica Digital.

## Ejecutar

```powershell
npm install
copy .env.example .env
npm run dev
```

App local: `http://localhost:5173`

## Variables

```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=dev-local-api-key
```

El valor de `VITE_API_KEY` debe coincidir con `APP_API_KEY` en el backend.

## Checks

```powershell
npm run lint
npm run build
```
