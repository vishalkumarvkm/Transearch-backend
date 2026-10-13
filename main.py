import os
import time
import datetime
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Request, Response, Depends, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import (
    CallInteractionCreate,
    CallInteraction,
    LoginRequest,
    LoginResponse,
    AdminUser,
    UserCreate,
    UserResponse,
    DeleteAccountRequest,
    CallStats
)
from geo_service import (
    get_client_ip,
    resolve_geo_location,
    get_device_type,
    format_duration
)
from database import (
    init_db,
    save_interaction,
    get_all_interactions,
    get_interaction_by_id,
    delete_interaction,
    compute_stats,
    create_user,
    delete_user,
    get_all_users,
    check_mongo_connection,
    DB_NAME,
    MONGODB_URI
)
from auth import (
    verify_credentials,
    create_access_token,
    verify_token,
    get_current_admin
)

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MongoDB, collections and indexes
    print("🚀 Starting TRANSEARCH Voice Intelligence API Server...")
    init_db()
    yield
    print("🛑 Shutting down TRANSEARCH Voice Intelligence API Server...")

app = FastAPI(
    title="TRANSEARCH Executive Voice Intelligence API",
    description="""
# TRANSEARCH Voice Intelligence & Call Audit API (Python + MongoDB)

### Available Modules:
- **Account Management**: Create and delete consultant/admin accounts in MongoDB with salted SHA-256 encryption.
- **Authentication**: Consultant sign-in and HMAC-SHA256 session token management.
- **Voice Calls & Transcripts**: Live call dialogue ingestion with automatic Client IP and Geolocation resolution.
- **Admin Intelligence & Analytics**: Filtered call logs, full transcripts, and real-time KPI metrics.
    """,
    version="2.1.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Account Management",
            "description": "Endpoints to create, list, and delete consultant accounts in MongoDB."
        },
        {
            "name": "Authentication",
            "description": "Consultant sign-in, session verification, and sign-out."
        },
        {
            "name": "Voice Calls & Transcripts",
            "description": "Ingest and audit live voice interactions with caller IP and geolocation."
        },
        {
            "name": "Admin Call Intelligence",
            "description": "Retrieve audited call transcripts, search records, and analyze executive KPIs."
        },
        {
            "name": "System Health",
            "description": "Health checks and MongoDB connection diagnostics."
        }
    ]
)

# CORS configuration
origins_env = os.getenv("ALLOWED_ORIGINS", "https://transearchai.com,https://www.transearchai.com,http://187.126.124.110:3000,http://localhost:3000,http://127.0.0.1:3000,http://localhost:3005")
allowed_origins = [o.strip() for o in origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# 1. System Health
# -------------------------------------------------------------
@app.get("/api/health", tags=["System Health"], summary="Check service and MongoDB health")
async def health_check():
    """Verify backend status and active MongoDB database connection."""
    return {
        "status": "online",
        "service": "TRANSEARCH Executive Voice Intelligence Backend",
        "database": {
            "type": "MongoDB",
            "connected": check_mongo_connection(),
            "databaseName": DB_NAME,
            "uri": MONGODB_URI.split("@")[-1] if "@" in MONGODB_URI else MONGODB_URI
        },
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

# -------------------------------------------------------------
# 2. Account Management Endpoints
# -------------------------------------------------------------
@app.post(
    "/api/auth/create-account",
    tags=["Account Management"],
    summary="Create a new consultant/admin account in MongoDB",
    status_code=status.HTTP_201_CREATED
)
@app.post(
    "/api/auth/register",
    tags=["Account Management"],
    summary="Register account (alias for create-account)",
    status_code=status.HTTP_201_CREATED
)
@app.post(
    "/api/admin/users",
    tags=["Account Management"],
    summary="Admin account creation endpoint",
    status_code=status.HTTP_201_CREATED
)
async def create_account(account_data: UserCreate):
    """
    **Create Account**:
    - Validates unique username.
    - Encrypts password using SHA-256 with a unique 16-byte random salt.
    - Saves user record into MongoDB `users` collection.
    """
    if len(account_data.password.strip()) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )

    try:
        user = create_user(
            username=account_data.username,
            email=account_data.email,
            password=account_data.password,
            role=account_data.role or "consultant"
        )
        return {
            "success": True,
            "message": f"Account '{account_data.username}' created successfully in MongoDB.",
            "user": user
        }
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err)
        )

@app.delete(
    "/api/admin/users/{username}",
    tags=["Account Management"],
    summary="Delete an account by username from MongoDB"
)
@app.delete(
    "/api/auth/delete-account",
    tags=["Account Management"],
    summary="Delete account (query parameter or username)"
)
async def remove_account(
    username: Optional[str] = None,
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """
    **Delete Account**:
    - Permanently deletes the specified user account from the MongoDB `users` collection.
    - Requires administrator authentication (`Authorization: Bearer <token>` or admin cookie).
    - Prevents accidental deletion of the primary root superadmin (`admin@transearch.com`).
    """
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account username is required for deletion."
        )

    try:
        deleted = delete_user(username)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account '{username}' not found in MongoDB."
            )
        return {
            "success": True,
            "message": f"Account '{username}' has been permanently deleted from MongoDB."
        }
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(err)
        )

@app.get(
    "/api/admin/users",
    tags=["Account Management"],
    summary="List all consultant accounts registered in MongoDB"
)
async def list_accounts(admin: Dict[str, Any] = Depends(get_current_admin)):
    """Retrieve all accounts registered in MongoDB (omits sensitive password hashes)."""
    return {
        "success": True,
        "users": get_all_users()
    }

# -------------------------------------------------------------
# 3. Authentication Endpoints
# -------------------------------------------------------------
@app.post(
    "/api/auth/login",
    tags=["Authentication"],
    summary="Consultant sign-in against MongoDB"
)
async def login(credentials: LoginRequest, response: Response):
    """
    **Consultant Sign In**:
    - Verifies password against hashed credentials stored in MongoDB.
    - Issues an HMAC-SHA256 session token valid for 7 days.
    - Sets secure HTTP-only cookie `transearch_admin_session`.
    """
    user = verify_credentials(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Access is restricted to authorized TRANSEARCH consultants."
        )

    token = create_access_token(user["username"], user.get("role", "consultant"))

    # Set HTTP-only session cookie
    response.set_cookie(
        key="transearch_admin_session",
        value=token,
        httponly=True,
        max_age=7 * 24 * 3600,
        samesite="lax",
        secure=False
    )

    return {
        "success": True,
        "token": token,
        "user": user
    }

@app.post(
    "/api/auth/logout",
    tags=["Authentication"],
    summary="Consultant sign-out"
)
async def logout(response: Response):
    """Clear consultant session cookie."""
    response.delete_cookie(key="transearch_admin_session", path="/")
    return {"success": True, "message": "Logged out successfully"}

@app.get(
    "/api/auth/me",
    tags=["Authentication"],
    summary="Verify current session token"
)
async def check_auth(request: Request):
    """Inspect and validate current session token."""
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()

    if not token:
        token = request.cookies.get("transearch_admin_session")

    session = verify_token(token)
    if not session:
        return {"authenticated": False}

    return {
        "authenticated": True,
        "user": {
            "username": session.get("username"),
            "role": session.get("role")
        }
    }

# -------------------------------------------------------------
# 4. Voice Calls & Transcripts Ingestion
# -------------------------------------------------------------
@app.post(
    "/api/web-transcript",
    tags=["Voice Calls & Transcripts"],
    summary="Ingest voice call transcript & capture audit data in MongoDB"
)
@app.post(
    "/api/calls",
    tags=["Voice Calls & Transcripts"],
    summary="Alias for /api/web-transcript"
)
async def record_interaction(payload: CallInteractionCreate, request: Request):
    """
    **Live Call Ingestion**:
    - Captures caller IP address from headers (`x-forwarded-for`, `cf-connecting-ip`, `x-real-ip`).
    - Resolves network Geolocation (City, Region, Country, Timezone).
    - Detects caller device type (`Desktop` vs `Mobile` vs `Tablet`).
    - Saves dialogue turns and candidate lead dossier into MongoDB `interactions` collection.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    
    # 1. Capture Client IP & Resolve Geolocation
    ip = get_client_ip(request)
    geo = await resolve_geo_location(ip, request)
    
    raw_user_agent = payload.user_agent or request.headers.get("user-agent")
    device_type = get_device_type(raw_user_agent)

    # 2. Timing & Dates
    if payload.started_at:
        try:
            start_dt = datetime.datetime.fromisoformat(payload.started_at.replace("Z", "+00:00"))
        except Exception:
            start_dt = now
    else:
        start_dt = now

    date_str = start_dt.strftime("%Y-%m-%d")
    time_str = start_dt.strftime("%H:%M:%S")

    duration = float(payload.duration_secs or 0.0)
    dur_formatted = format_duration(duration)

    call_id = f"call_{int(time.time() * 1000)}_{os.urandom(3).hex()}"
    session_id = payload.session_id or call_id

    # 3. Candidate Info & Status
    lead = payload.lead_info or {}
    has_lead = bool(lead.get("name") or lead.get("email") or lead.get("phone"))
    status_label = "Lead Captured" if has_lead else "Completed"

    segments_data = [s.model_dump() for s in payload.segments] if payload.segments else []

    # 4. Construct Call Document
    doc: Dict[str, Any] = {
        "id": call_id,
        "sessionId": session_id,
        "date": date_str,
        "time": time_str,
        "startedAt": start_dt.isoformat(),
        "endedAt": payload.ended_at or now.isoformat(),
        "durationSecs": duration,
        "durationFormatted": dur_formatted,
        "ipAddress": ip,
        "geoLocation": geo.model_dump(),
        "agentId": payload.agent_id or "transearch-general",
        "agentName": payload.agent_name or "Sara (TRANSEARCH International)",
        "mandate": payload.industry or "Executive Search & Leadership Advisory",
        "route": payload.source_url or "/talktotransearch",
        "userAgent": raw_user_agent,
        "deviceType": device_type,
        "candidateInfo": lead if lead else None,
        "segments": segments_data,
        "totalTurns": len(segments_data),
        "status": status_label,
        "createdAt": now.isoformat()
    }

    # 5. Persist to MongoDB
    saved = save_interaction(doc)

    print(f"✅ [TRANSEARCH Backend] Persisted call {call_id} from {ip} ({geo.city}, {geo.country})")

    return {
        "success": True,
        "message": "Call interaction persisted into MongoDB database successfully",
        "id": call_id,
        "sessionId": session_id,
        "ipAddress": ip,
        "location": f"{geo.city}, {geo.country}"
    }

# -------------------------------------------------------------
# 5. Admin Call Intelligence & Analytics
# -------------------------------------------------------------
@app.get(
    "/api/admin/calls",
    tags=["Admin Call Intelligence"],
    summary="List audited calls with search and filtering from MongoDB"
)
async def list_calls(
    search: Optional[str] = Query(None, description="Search query across candidate name, notes, IP, location, transcript words"),
    agent: Optional[str] = Query(None, description="Filter by agent id or name"),
    status: Optional[str] = Query(None, description="Filter by status (Lead Captured / Completed)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Query call logs from MongoDB with full-text search, agent filtering, and live analytics."""
    calls = get_all_interactions(
        agent_filter=agent,
        status_filter=status,
        search_query=search,
        skip=skip,
        limit=limit
    )
    stats = compute_stats()

    return {
        "success": True,
        "calls": calls,
        "stats": stats
    }

@app.get(
    "/api/admin/calls/{call_id}",
    tags=["Admin Call Intelligence"],
    summary="Fetch single interaction record by ID or Session ID"
)
async def get_call_detail(
    call_id: str,
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Retrieve full call dossier including network metadata and complete turn-by-turn dialogue."""
    call = get_interaction_by_id(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call record not found")
    return {"success": True, "call": call}

@app.delete(
    "/api/admin/calls/{call_id}",
    tags=["Admin Call Intelligence"],
    summary="Delete a call record from MongoDB"
)
async def delete_call_record(
    call_id: str,
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Permanently delete an interaction record from MongoDB."""
    success = delete_interaction(call_id)
    if not success:
        raise HTTPException(status_code=404, detail="Call record not found or could not be deleted")
    return {"success": True, "message": "Interaction record deleted from MongoDB"}

@app.get(
    "/api/admin/stats",
    tags=["Admin Call Intelligence"],
    summary="Get aggregate call KPIs (Total calls, duration, leads, locations)"
)
async def get_dashboard_stats(
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Retrieve aggregate statistics computed across MongoDB collections."""
    return {"success": True, "stats": compute_stats()}
