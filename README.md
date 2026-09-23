# Capacitacion AI

Microservicio de IA en Python para integrarlo con una aplicación Next.js. Expone FastAPI y transforma el streaming NDJSON de Ollama en eventos SSE.

## Requisitos

- Python 3.11+
- [Ollama](https://ollama.com/download) instalado y ejecutándose
- Modelo descargado: `ollama pull llama3.2`

## Instalación local

En PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

El servicio queda disponible en `http://localhost:8000`. La documentación interactiva está en `http://localhost:8000/docs`.

## API

### `GET /health`

Comprueba que el proceso está levantado. No necesita Ollama.

### `POST /api/chat`

Request:

```json
{
  "messages": [
    {"role": "user", "content": "Explícame qué es una API"}
  ]
}
```

La respuesta es `text/event-stream`. Cada evento `token` contiene `{"content":"..."}` y el último evento es `done`. Cuando Ollama falla se envía un evento `error`.

Ejemplo desde Next.js:

```ts
const response = await fetch(`${process.env.PYTHON_AI_URL}/api/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ messages }),
});

const reader = response.body!.getReader();
```

En producción, define `AI_CORS_ORIGINS` con el dominio real del frontend y mantén el servicio Python detrás de tu proxy o backend principal.

## Pruebas

```powershell
python -m pytest
```

Las pruebas del endpoint de chat requieren que Ollama esté disponible; la prueba incluida cubre el health check sin depender del modelo.