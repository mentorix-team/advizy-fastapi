# Advizy FastAPI Microservice

A FastAPI application that integrates embeddings, Qdrant vector database, and Groq API for AI-powered advice and recommendations.

## Prerequisites

- Python 3.10.11 or higher
- Docker for containerized deployment

## Installation

### Local Development Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/mentorix-team/advizy-fastapi.git
   cd advizy-fastapi
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies:**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Set environment variables:**

   Create a `.env` file in the root directory or export the variables:

   ```bash
   QDRANT_URL=your_qdrant_cloud_url
   QDRANT_API_KEY=your_qdrant_api_key
   ```

6. **Run the application:**

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`.

### Docker Setup

##. install docker
```bash
#check version
docker --version
```

1. **Pull the Docker image:**

   ```bash
   docker pull sidhu18/advizy-fastapi:latest
   ```

2. **Create environment file:**

   Create a `.env` file with your environment variables:

   ```env
   QDRANT_URL=your_qdrant_cloud_url
   QDRANT_API_KEY=your_qdrant_api_key
   ```

3. **Run the container:**

   ```bash
   docker run -d \
     -p 8000:8000 \
     --env-file .env \
     --name advizy-fastapi \
     sidhu18/advizy-fastapi:latest
   ```

4. **Verify the container is running:**

   ```bash
   docker ps
   ```

## Useful Docker Commands

- **Stop the container:**
  ```bash
  docker stop advizy-fastapi
  ```

- **Restart the container:**
  ```bash
  docker start advizy-fastapi
  ```

- **Remove the container:**
  ```bash
  docker rm -f advizy-fastapi
  ```

## Configuration

The application requires the following environment variables:

- `QDRANT_URL`: URL of your Qdrant cloud instance
- `QDRANT_API_KEY`: API key for Qdrant authentication


## API Endpoints

Once the application is running, you can access the API documentation at `http://localhost:8000/docs` to explore available endpoints.
