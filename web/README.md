# SudokuSolver Web Application

This directory contains the web frontend and backend components for the SudokuSolver application.

## Architecture

The web application consists of:

- **Backend**: FastAPI application providing REST API endpoints
- **Frontend**: React application with TypeScript
- **Nginx**: Reverse proxy serving the frontend and routing API calls to the backend
- **Redis**: Session storage for stepwise solving (experimental feature)

## Project Structure

```
web/
├── backend/           # FastAPI backend service
│   ├── app.py        # Main FastAPI application
│   ├── step_solver.py # Step-wise solving logic (stub)
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile    # Backend container configuration
├── frontend/         # React frontend
│   └── Dockerfile    # Multi-stage frontend container
├── nginx/            # Nginx configuration
│   └── nginx.conf    # Reverse proxy configuration
├── docker-compose.yml # Orchestration configuration (includes Redis)
└── README.md         # This file
```

## Local Development

### Prerequisites

- Docker and Docker Compose installed
- Node.js 20+ (for frontend development)
- Python 3.12+ (for backend development)
- Redis (included via Docker Compose; for local dev, see below)

### Redis Setup

**Using Docker Compose (Recommended):**
Redis is automatically started when you run `docker-compose up`. No additional setup needed.

**For Local Development (Backend Only):**
If running the backend locally without Docker:

1. **Install Redis locally:**
   - Windows: `choco install redis` or use Docker: `docker run -d -p 6379:6379 redis:7-alpine`
   - macOS: `brew install redis` then `brew services start redis`
   - Linux: `sudo apt-get install redis-server` then `sudo systemctl start redis`

2. **Verify Redis is running:**
   ```bash
   redis-cli ping  # Should return "PONG"
   ```

3. **Set environment variable (optional):**
   ```bash
   export REDIS_URL=redis://localhost:6379/0  # Default value
   ```

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

1. **Start Redis (required for session endpoints):**
   ```bash
   # Option 1: Using Docker Compose (recommended)
   cd web
   docker compose up redis -d
   
   # Option 2: Using Docker directly
   docker run -d --name redis-sudoku -p 6379:6379 redis:7-alpine
   
   # Option 3: Using local Redis installation
   redis-server  # Must be installed locally
   ```

2. **Backend only:**
   ```bash
   cd web/backend
   pip install -r requirements.txt  # Installs redis package
   python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
   ```
   
   **Note:** The full solve endpoint (`/api/solve`) will work without Redis, but session endpoints require Redis to be running.

3. **Frontend only:**
   ```bash
   cd web/frontend
   npm install
   npm run dev
   ```

## API Endpoints

### Health Check
- **GET** `/api/healthz`
- Returns: `{"status": "ok"}`

### Solve Sudoku (Full Solve)
- **POST** `/api/solve`
- Body: `{"grid": number[][], "debug_level": number}`
- Returns: `{"solution": number[][] | null, "success": boolean, "message": "string"}`
- Fully integrated with core SudokuSolver engine

### Session-Based Stepwise Solving (Experimental)

**Create Session:**
- **POST** `/api/sessions`
- Body: `{"grid": number[][], "debug_level": number}`
- Returns: `{"session_id": "string"}`
- Creates a new solving session and stores initial grid state in Redis

**Apply Step:**
- **POST** `/api/sessions/{session_id}/step`
- Returns: `{"grid": number[][], "step": {"rule": string, "row": number, "col": number, "value": number}, "done": boolean}`
- Applies one solving step and updates grid state in Redis
- Returns updated grid, step information, and completion status

**Delete Session:**
- **DELETE** `/api/sessions/{session_id}`
- Returns: `{"deleted": boolean}`
- Removes session from Redis storage

**Note:** Currently uses stub step solver (`step_solver.py`). Ready for integration with real step-wise SudokuSolver logic.

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

## Features

### Current Features
- ✅ Full puzzle solving via `/api/solve` endpoint
- ✅ Stepwise solving via session endpoints (experimental)
- ✅ Redis-backed session storage
- ✅ Grid-based input/output with validation
- ✅ Debug level support (0-3)
- ✅ Visual grid display with 3×3 box boundaries
- ✅ Sample puzzle loading
- ✅ Error handling and validation

### Future Enhancements
1. Replace stub step solver with real step-wise logic
2. Add session TTL for auto-cleanup
3. Add authentication and user management
4. Implement file upload for puzzle images
5. Add database persistence for puzzle history
6. Set up HTTPS with SSL certificates
7. Add monitoring and logging
8. Implement CI/CD pipeline
9. Add undo/redo functionality for stepwise solving
