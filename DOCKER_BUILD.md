# Docker Build Instructions

## Building the Images

To build the Docker images for this project, you need to build from the **project root directory**.

### Backend Image

```bash
docker build -f Backend/Dockerfile -t alexlopez7498/pl_predictor_backend:latest .
```

### Frontend Image

```bash
docker build -f frontend/Dockerfile -t alexlopez7498/pl_predictor_frontend:latest .
```

### Pushing to Docker Hub

After building, push the images to Docker Hub:

```bash
docker push alexlopez7498/pl_predictor_backend:latest
docker push alexlopez7498/pl_predictor_frontend:latest
```

## Running with Docker Compose

Once images are pushed to Docker Hub, anyone can run the application with:

1. **Create a `.env` file** in the project root:
   ```
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=your_db_name
   DB_PORT=5432
   ```

2. **Run docker-compose**:
   ```bash
   docker-compose up -d
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## What's Included in the Images

- **Backend image**: Includes all Python dependencies, application code, ML models, and required data files
- **Frontend image**: Includes the built Next.js application
- **No local files needed**: Everything is self-contained in the images (except for the `.env` file)

