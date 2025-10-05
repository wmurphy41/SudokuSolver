# SudokuSolver Web Application

This directory contains the web frontend and backend components for the SudokuSolver application.

## Architecture

The web application consists of:

- **Backend**: FastAPI application providing REST API endpoints
- **Frontend**: React application (to be scaffolded with Vite)
- **Nginx**: Reverse proxy serving the frontend and routing API calls to the backend

## Project Structure

```
web/
├── backend/           # FastAPI backend service
│   ├── app.py        # Main FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile    # Backend container configuration
├── frontend/         # React frontend (to be created)
│   └── Dockerfile    # Multi-stage frontend container
├── nginx/            # Nginx configuration
│   └── nginx.conf    # Reverse proxy configuration
├── docker-compose.yml # Orchestration configuration
└── README.md         # This file
```

## Local Development

### Prerequisites

- Docker and Docker Compose installed
- Node.js 20+ (for frontend development)
- Python 3.12+ (for backend development)

### Running the Application

1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost/api/healthz

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Development Mode

For active development, you may want to run services separately:

1. **Backend only:**
   ```bash
   cd web/backend
   pip install -r requirements.txt
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend only:**
   ```bash
   cd web/frontend
   npm install
   npm run dev
   ```

## API Endpoints

### Health Check
- **GET** `/api/healthz`
- Returns: `{"status": "ok"}`

### Solve Sudoku (Placeholder)
- **POST** `/api/solve`
- Body: `{"puzzle": "string", "difficulty": "easy"}`
- Returns: `{"solution": "string", "success": true, "message": "string"}`

## Deployment

### AWS Lightsail Deployment

1. **Prepare the server:**
   ```bash
   # Install Docker and Docker Compose
   sudo apt update
   sudo apt install docker.io docker-compose-plugin
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker $USER
   ```

2. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd SudokuSolver
   ```

3. **Build and run:**
   ```bash
   cd web
   docker-compose up --build -d
   ```

4. **Configure firewall (if needed):**
   ```bash
   sudo ufw allow 80
   sudo ufw allow 443  # For HTTPS later
   ```

### Environment Variables

For production deployment, consider setting these environment variables in `docker-compose.yml`:

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - ENVIRONMENT=production
  # Add other production-specific variables
```

## Troubleshooting

### Common Issues

1. **Port 80 already in use:**
   - Change the port mapping in `docker-compose.yml`
   - Or stop the conflicting service

2. **Backend not starting:**
   - Check logs: `docker-compose logs backend`
   - Ensure all dependencies are installed

3. **Frontend build failing:**
   - Check logs: `docker-compose logs web`
   - Ensure Node.js version compatibility

### Logs

View logs for all services:
```bash
docker-compose logs -f
```

View logs for specific service:
```bash
docker-compose logs -f backend
docker-compose logs -f web
```

## Next Steps

1. Scaffold the React frontend with Vite
2. Integrate the actual SudokuSolver backend logic
3. Add authentication and user management
4. Implement file upload for puzzle images
5. Add database persistence
6. Set up HTTPS with SSL certificates
7. Add monitoring and logging
8. Implement CI/CD pipeline
