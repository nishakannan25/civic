# Civic AI - Local Development & Docker Deployment

## 1. Local Infrastructure with Docker Compose

Civic AI uses Docker Compose to run the FastAPI backend alongside the PostgreSQL database with automated health monitoring.

### Starting Services
From the repository root:
```bash
# Navigate to infrastructure directory
cd infrastructure

# Start PostgreSQL and FastAPI in background
docker compose up -d --build
```

### Checking Status & Logs
```bash
# View container status
docker compose ps

# Follow backend logs
docker compose logs -f backend

# Follow postgres logs
docker compose logs -f postgres
```

### Stopping Services
```bash
docker compose down

# To clean database volumes as well:
docker compose down -v
```

---

## 2. Network Configuration for Mobile Clients

Depending on the mobile execution environment, configure `API_BASE_URL` in `mobile/lib/core/config/app_config.dart`:

| Environment | API Base URL | Explanation |
|---|---|---|
| **Android Emulator** | `http://10.0.2.2:8000` | Android emulator alias for host machine's `127.0.0.1` |
| **iOS Simulator** | `http://127.0.0.1:8000` | iOS simulator shares localhost network directly with host |
| **macOS / Linux Desktop** | `http://127.0.0.1:8000` | Local desktop app accesses loopback directly |
| **Flutter Web** | `http://localhost:8000` | Browser runs on host |
| **Physical Phone (Wi-Fi)** | `http://<YOUR_LAN_IP>:8000` | e.g. `http://192.168.1.150:8000` (ensure firewall allows 8000) |

---

## 3. Environment Variables Reference

| Variable | Description | Example / Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://civic_user:civic_password@localhost:5432/civic_ai_db` |
| `JWT_SECRET` | Secret key for signing auth tokens | Min 32 random characters |
| `JWT_ALGORITHM` | Cryptographic algorithm for JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `1440` (24h) |
| `AI_SERVICE_URL` | Microservice URL for vision AI (Phase 4/5) | `http://localhost:8001` |
| `COMMUNITY_RADIUS` | Geofence radius for neighbor verification | `500.0` meters |
