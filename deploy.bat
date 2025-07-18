@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    Interview System Docker Deploy Script
echo ========================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker not found. Please install Docker Desktop first.
    echo Download: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose not found. Please ensure Docker Desktop is installed.
    pause
    exit /b 1
)

echo [INFO] Docker environment check passed

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "backend\uploads" mkdir backend\uploads
if not exist "backend\uploads\resumes" mkdir backend\uploads\resumes
if not exist "backend\uploads\audio" mkdir backend\uploads\audio
if not exist "backend\uploads\video" mkdir backend\uploads\video
if not exist "backend\logs" mkdir backend\logs
if not exist "backend\temp" mkdir backend\temp

REM Check required files
if not exist "docker-compose.yml" (
    echo [ERROR] docker-compose.yml file not found
    echo Please ensure all Docker configuration files are created
    pause
    exit /b 1
)

if not exist "backend\Dockerfile" (
    echo [ERROR] backend\Dockerfile file not found
    pause
    exit /b 1
)

if not exist "frontend\Dockerfile" (
    echo [ERROR] frontend\Dockerfile file not found
    pause
    exit /b 1
)

echo [INFO] File check passed

REM Handle command line arguments
if "%1"=="build" goto build
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="cleanup" goto cleanup
if "%1"=="help" goto help
if "%1"=="" goto deploy

:help
echo.
echo Usage: deploy.bat [command]
echo.
echo Commands:
echo   deploy    - Full deployment (default)
echo   build     - Build images only
echo   start     - Start services
echo   stop      - Stop services
echo   restart   - Restart services
echo   status    - Show service status
echo   logs      - Show service logs
echo   cleanup   - Clean Docker resources
echo   help      - Show help information
echo.
echo Examples:
echo   deploy.bat          # Full deployment
echo   deploy.bat logs     # Show logs
echo   deploy.bat cleanup  # Clean resources
echo.
pause
exit /b 0

:deploy
echo [INFO] Starting full deployment...
goto generate_env

:generate_env
echo [INFO] Generating production environment configuration...

REM Generate random secret key
set SECRET_KEY=interview_system_secret_key_%RANDOM%%RANDOM%%RANDOM%

REM Create backend production environment configuration
(
echo # Production Environment Configuration
echo PROJECT_NAME=Interview System API
echo API_V1_STR=/api/v1
echo.
echo # Server Configuration
echo SERVER_HOST=0.0.0.0
echo SERVER_PORT=8000
echo.
echo # Database Configuration
echo DATABASE_URL=sqlite:///./app.db
echo.
echo # JWT Authentication Configuration
echo SECRET_KEY=!SECRET_KEY!
echo ALGORITHM=HS256
echo ACCESS_TOKEN_EXPIRE_MINUTES=1440
echo.
echo # File Upload Configuration
echo UPLOAD_FOLDER=./uploads
echo MAX_FILE_SIZE=10485760
echo.
echo # CORS Configuration (modify according to your domain)
echo BACKEND_CORS_ORIGINS=http://localhost,http://127.0.0.1,http://your-domain.com
) > backend\.env.production

echo [SUCCESS] Environment configuration generated
echo [WARNING] Please modify backend\.env.production according to your needs
goto build

:build
echo [INFO] Building Docker images...
docker-compose build --no-cache
if %errorlevel% neq 0 (
    echo [ERROR] Image build failed
    pause
    exit /b 1
)
echo [SUCCESS] Images built successfully
if "%1"=="build" goto end
goto start_services

:start_services
:start
echo [INFO] Starting services...
docker-compose down >nul 2>nul
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Service startup failed
    echo View detailed logs:
    docker-compose logs
    pause
    exit /b 1
)
echo [SUCCESS] Services started successfully
goto check_services

:check_services
echo [INFO] Checking service status...
timeout /t 10 /nobreak >nul

docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Services are running normally
    echo.
    echo ========================================
    echo         Service Access URLs
    echo ========================================
    echo Frontend: http://localhost:80
    echo Backend API: http://localhost:8000
    echo API Docs: http://localhost:8000/api/v1/docs
    echo Health Check: http://localhost:8000/api/v1/health
    echo.
    echo ========================================
    echo         Common Commands
    echo ========================================
    echo View logs: deploy.bat logs
    echo Stop services: deploy.bat stop
    echo Restart services: deploy.bat restart
    echo.
) else (
    echo [ERROR] Service startup failed, please check logs:
    docker-compose logs
    pause
    exit /b 1
)
goto end

:stop
echo [INFO] Stopping services...
docker-compose down
echo [SUCCESS] Services stopped
goto end

:restart
echo [INFO] Restarting services...
docker-compose restart
goto check_services

:status
docker-compose ps
goto end

:logs
docker-compose logs -f
goto end

:cleanup
echo [INFO] Cleaning Docker resources...
docker-compose down -v
docker image prune -f
echo [SUCCESS] Cleanup completed
goto end

:end
if "%1"=="" pause
exit /b 0