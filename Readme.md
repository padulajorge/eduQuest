# eduQuest

API construida con FastAPI para gestionar interacciones de chat.

## Requisitos

- Python 3.8 o superior
- [pip](https://pip.pypa.io/en/stable/)

## Instalación

1. Clona el repositorio:
   ```sh
   git clone https://github.com/padulajorge/eduQuest.git
   cd eduQuest
   ```

2. Crea y activa un entorno virtual:
   ```sh
   python -m venv venv
   venv\Scripts\activate   # En Windows
   ```

3. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```

4. Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
   ```
   OPENROUTER_API_KEY=tu-api-key
   ```

## Uso

Para iniciar el servidor en modo desarrollo:

```sh
uvicorn main:app --reload
```

La API estará disponible en [http://localhost:8000](http://localhost:8000).

## Endpoints principales

- `/chat/*` — Endpoints relacionados con el chat (ver detalles en `routers/chatApi.py`).

## Notas

- Asegúrate de no compartir tu archivo `.env` ni tu API key.
- Puedes modificar la configuración de rutas en `main.py`.

## Licencia

MIT