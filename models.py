from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

class TranscriptSegment(BaseModel):
    speaker: str
    text: str
    timestamp: Optional[Union[float, int, str]] = None

class CandidateInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    currentRole: Optional[str] = None
    notes: Optional[str] = None

class GeoLocation(BaseModel):
    ip: str
    city: Optional[str] = "Global Visitor"
    region: Optional[str] = None
    country: Optional[str] = "International"
    countryCode: Optional[str] = "GLOBAL"
    timezone: Optional[str] = None
    isLocal: bool = False

class CallInteractionCreate(BaseModel):
    session_id: Optional[str] = None
    agent_id: Optional[str] = "transearch-general"
    agent_name: Optional[str] = "Sara (TRANSEARCH International)"
    industry: Optional[str] = "Executive Search & Leadership Advisory"
    language: Optional[str] = "English"
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    duration_secs: Optional[float] = 0.0
    lead_info: Optional[Dict[str, Any]] = None
    segments: Optional[List[TranscriptSegment]] = []
    source_url: Optional[str] = "/talktotransearch"
    user_agent: Optional[str] = None

class CallInteraction(BaseModel):
    id: str
    sessionId: str
    date: str
    time: str
    startedAt: str
    endedAt: Optional[str] = None
    durationSecs: float = 0.0
    durationFormatted: str = "0s"
    ipAddress: str
    geoLocation: GeoLocation
    agentId: str
    agentName: str
    mandate: str
    route: str
    userAgent: Optional[str] = None
    deviceType: str = "Desktop"
    candidateInfo: Optional[CandidateInfo] = None
    segments: List[TranscriptSegment] = []
    totalTurns: int = 0
    status: str = "Completed"
    createdAt: str

class LoginRequest(BaseModel):
    username: str
    password: str

class AdminUser(BaseModel):
    username: str
    email: Optional[str] = None
    role: str = "superadmin"

class LoginResponse(BaseModel):
    success: bool
    token: str
    user: AdminUser

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: str = "consultant"

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    role: str = "consultant"
    createdAt: str

class DeleteAccountRequest(BaseModel):
    username: str
    password: Optional[str] = None

class CallStats(BaseModel):
    totalCalls: int
    totalDurationSecs: float
    totalDurationFormatted: str
    totalLeadsCaptured: int
    uniqueLocationsCount: int
    topAgents: List[Dict[str, Any]]
