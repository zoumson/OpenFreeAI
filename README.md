# OpenFreeAI

OpenFreeAI is a local AI chat platform with a web-based interface, designed for both regular users and administrators to interact with and manage AI models dynamically.

## Features

- **User Chat Interface**: Ask questions to AI models via a web-based client.
- **Admin Interface**: Upload JSON model files, clear models, and manage available models.
- **Dynamic Model Loading**: Users automatically see newly added models without restarting the client.
- **REST API Integration**: Communicates with the server via `/job/prompt` and `/model` endpoints.
- **Asynchronous Task Processing**: Handles AI prompt processing in the background using Celery.
- **Containerized Deployment**: Easily run server, task queue, and client interfaces in Docker containers.

## Architecture & Services

### Server Side

- **server**: Flask API backend served with Gunicorn.
- **celery_worker**: Processes prompt tasks asynchronously, ensuring fast and non-blocking responses.
- **redis**: Task broker for Celery, used for asynchronous queue management.
- **mysql**: Persistent storage for server data.

### Client Side

- **client_user**: Gradio-based UI for end-users to interact with models.
- **client_admin**: Gradio-based admin panel for model management (uploading and clearing models).

### Docker Services

| Service         | Description                              |
| --------------- | ---------------------------------------- |
| `mysql`         | MySQL database for persistent storage    |
| `redis`         | Redis broker for Celery tasks            |
| `server`        | Flask API backend served via Gunicorn    |
| `celery_worker` | Background task processor for AI prompts |
| `client_user`   | Frontend interface for regular users     |
| `client_admin`  | Frontend interface for administrators    |

## Tech Stack

- **Python 3.11**
- **Flask** – API server
- **Gradio 4.44.1** – User/admin interfaces
- **Celery** – Asynchronous task processing
- **Gunicorn** – Production-ready WSGI server
- **Docker & Docker Compose** – Containerized deployment
- **Redis** – Celery message broker
- **MySQL** – Persistent database

## Getting Started

1. **Clone the repository with submodules**:

   ```bash
   git clone --recurse-submodules <repo_url>
   ```

2. **Build and start the Docker containers**:

   ```bash
   docker-compose up --build
   ```

3. **Access the UI**:
   - **Client User**: `http://localhost:<USER_CLIENT_PORT>`
   - **Client Admin**: `http://localhost:<ADMIN_CLIENT_PORT>`

## Notes

- Admin features require `TRUSTED_MODE=True` in `client/config.py`.
- Models must be uploaded in JSON format.
- Client interfaces dynamically refresh the model list to reflect newly uploaded models.

## License

[MIT](LICENSE)
