# TRANSEARCH Executive Voice Intelligence — Python & MongoDB Backend

High-performance **FastAPI** backend powering the TRANSEARCH Executive Voice Agents platform and the Call Audit Intelligence Dashboard with **MongoDB** persistence.

---

## 🐳 Docker Container Stack

The backend includes a complete **Docker Compose** environment orchestrating:
1. **`transearch-mongodb`** (`mongo:7.0`): Dedicated MongoDB instance with persistent volume storage (`transearch_mongodb_data`).
2. **`transearch-backend`** (Python 3.11 + FastAPI): API server with live volume reload and auto-seeding.
3. **`transearch-mongo-express`** (`mongo-express:latest`): Web GUI for inspecting MongoDB collections in your browser at `http://localhost:8081`.

### 🚀 Running with Docker Compose

Ensure Docker Desktop is running, then run:

```powershell
cd c:\Users\visha\Downloads\pravakta-main\backend
docker compose up --build -d
```
*(Or double-click [`start_docker.bat`](file:///c:/Users/visha/Downloads/pravakta-main/backend/start_docker.bat))*

### 🌐 Access Docker Services:
- **FastAPI API & Endpoints**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Mongo Express Web GUI**: [http://localhost:8081](http://localhost:8081)
- **MongoDB Direct Port**: `localhost:27017`

### 🛑 Useful Docker Commands:
- **View live streaming logs**:
  ```powershell
  docker compose logs -f
  ```
- **Stop all containers**:
  ```powershell
  docker compose down
  ```
  *(Or double-click [`stop_docker.bat`](file:///c:/Users/visha/Downloads/pravakta-main/backend/stop_docker.bat))*

---

## 🌟 Key Capabilities

1. **MongoDB Persistence**:
   - Persists every voice call interaction into MongoDB collection `interactions`.
   - Stores: Call ID, Session ID, Date, Exact Timestamp, Caller Client IP, Geolocation (City, Region, Country, Timezone), Spoken Duration, Agent Persona, Executive Mandate, Candidate Lead Dossier (Name, Email, Phone, Role, Notes), and Complete Dialogue Turns.
   - Automatic indexing on `id`, `sessionId`, `startedAt`, `agentId`, and `status`.

2. **User & Account Management**:
   - Dedicated `users` collection in MongoDB storing encrypted password hashes (SHA-256 with 16-byte random salt).
   - Dedicated endpoints to **Create Account** and **Delete Account**.
   - Built-in root administrator protection (prevents deletion of `admin@transearch.com`).

3. **Caller Network & Geolocation Extraction**:
   - Automatically parses client IP from `x-forwarded-for`, `cf-connecting-ip`, `x-real-ip`, or socket connection.
   - Resolves Geolocation (City, Country, Timezone) with sub-second caching.
   - Detects device type (`Desktop` / `Mobile` / `Tablet`) from User-Agent.

4. **Executive Authentication**:
   - HMAC-SHA256 cryptographically signed session tokens.
   - Secures all `/api/admin/*` data endpoints.
   - Default consultant credentials:
     - **Username**: `admin@transearch.com` (or `admin`)
     - **Password**: `transearch2025`

---

## 📡 API Endpoints Reference

### Account & Authentication Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/create-account` (or `/api/auth/register`) | **Create new consultant/admin account** in MongoDB |
| `DELETE` | `/api/admin/users/{username}` (or `/api/auth/delete-account`) | **Delete an account** from MongoDB (Admin protected) |
| `GET` | `/api/admin/users` | List all accounts registered in MongoDB |
| `POST` | `/api/auth/login` | Authenticates against MongoDB and issues access token |
| `GET` | `/api/auth/me` | Validates current session token |
| `POST` | `/api/auth/logout` | Clears consultant session |

### Voice Interactions & Call Audit Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health status and MongoDB connection verification |
| `POST` | `/api/web-transcript` | Ingests voice calls, captures IP & geo, and saves to MongoDB |
| `GET` | `/api/admin/calls` | Retrieves filtered calls with search and analytics metrics |
| `GET` | `/api/admin/calls/{id}`| Retrieves full interaction dossier and complete transcript |
| `DELETE`| `/api/admin/calls/{id}`| Deletes an interaction record from MongoDB |
| `GET` | `/api/admin/stats` | Computes live KPIs (Total calls, talk time, leads captured) |
