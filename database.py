import os
import hmac
import hashlib
import datetime
from typing import List, Dict, Any, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "transearch_voice_db")
DEFAULT_ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin@transearch.com")
DEFAULT_ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "transearch2025")

client: Optional[MongoClient] = None
db = None
interactions_col = None
users_col = None
is_mongo_connected = False

def check_mongo_connection() -> bool:
    return is_mongo_connected

# Fallback in-memory stores if MongoDB server is offline
IN_MEMORY_STORE: List[Dict[str, Any]] = []
IN_MEMORY_USERS: List[Dict[str, Any]] = []

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Generates a secure SHA-256 password hash with salt."""
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed, salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verifies a password against hash and salt."""
    expected = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hmac.compare_digest(hashed, expected)

def get_initial_seed_data() -> List[Dict[str, Any]]:
    """Initial representative TRANSEARCH call interactions."""
    now = datetime.datetime.now(datetime.timezone.utc)
    def sub_mins(mins: int):
        return (now - datetime.timedelta(minutes=mins)).isoformat()

    return [
        {
            "id": "call_seed_001",
            "sessionId": "sess_earc_amit_98231",
            "date": (now - datetime.timedelta(minutes=35)).strftime("%Y-%m-%d"),
            "time": "19:42:10",
            "startedAt": sub_mins(35),
            "endedAt": sub_mins(30),
            "durationSecs": 312.0,
            "durationFormatted": "5m 12s",
            "ipAddress": "103.21.124.66",
            "geoLocation": {
                "ip": "103.21.124.66",
                "city": "Gurgaon",
                "region": "Haryana",
                "country": "India",
                "countryCode": "IN",
                "timezone": "Asia/Kolkata",
                "isLocal": False
            },
            "agentId": "earc-amit",
            "agentName": "Sara (EARC Consultant)",
            "mandate": "Head – Analytics",
            "route": "/talktosara-amit",
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/133.0",
            "deviceType": "Desktop",
            "candidateInfo": {
                "name": "Amit Kumar",
                "email": "amit.kumar@analytics-lead.com",
                "phone": "+91 98112 45890",
                "currentRole": "VP Analytics & Risk Modelling",
                "notes": "Interested in EARC mandate. Discussed portfolio recovery models, team size of 24, and board reporting hierarchy."
            },
            "segments": [
                {"speaker": "Assistant", "text": "Hello Amit! I am Sara from TRANSEARCH International. We are conducting an executive search for the Head of Analytics appointment at Encore Asset Reconstruction Company. It is great to speak with you.", "timestamp": 1},
                {"speaker": "User", "text": "Hi Sara, thanks for reaching out. Yes, I saw the briefing note. Could you share more details about the primary challenges for the portfolio analytics team?", "timestamp": 8},
                {"speaker": "Assistant", "text": "Certainly Amit. The mandate oversees retail and SME NPA portfolios, predictive recovery scoring, and developing an enterprise data lake. The role reports directly to the MD & CEO.", "timestamp": 18},
                {"speaker": "User", "text": "That aligns well with my background in debt resolution analytics. What is the expected timeline for executive rounds?", "timestamp": 35},
                {"speaker": "Assistant", "text": "The search committee is scheduling leadership interactions for early next month. I have noted your interest and will coordinate with the Senior Partner at TRANSEARCH.", "timestamp": 49}
            ],
            "totalTurns": 5,
            "status": "Lead Captured",
            "createdAt": sub_mins(30)
        },
        {
            "id": "call_seed_002",
            "sessionId": "sess_indegene_david_4821",
            "date": (now - datetime.timedelta(minutes=140)).strftime("%Y-%m-%d"),
            "time": "18:05:40",
            "startedAt": sub_mins(140),
            "endedAt": sub_mins(134),
            "durationSecs": 374.0,
            "durationFormatted": "6m 14s",
            "ipAddress": "178.197.234.12",
            "geoLocation": {
                "ip": "178.197.234.12",
                "city": "Zurich",
                "region": "Zurich",
                "country": "Switzerland",
                "countryCode": "CH",
                "timezone": "Europe/Zurich",
                "isLocal": False
            },
            "agentId": "david-indegene",
            "agentName": "David (TRANSEARCH Lead)",
            "mandate": "AVP – Client Partner (Indegene)",
            "route": "/talktotransearch-david",
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/17.4",
            "deviceType": "Desktop",
            "candidateInfo": {
                "name": "David Schneider",
                "email": "david.schneider@lifesciences-exec.ch",
                "phone": "+41 44 215 8890",
                "currentRole": "Managing Director, Commercial Life Sciences",
                "notes": "Strong engagement regarding DACH pharma client expansion. Compensation expectations aligned with Swiss executive bands."
            },
            "segments": [
                {"speaker": "Assistant", "text": "Good day David. Welcome to TRANSEARCH International. I am briefing you on the AVP Client Partner position with Indegene for enterprise life sciences accounts across Switzerland and DACH.", "timestamp": 1},
                {"speaker": "User", "text": "Hello. Yes, I am familiar with Indegene’s digital health consulting practice. Are the target accounts primarily Big Pharma in Basel?", "timestamp": 9},
                {"speaker": "Assistant", "text": "Exactly David. The remit anchors top-tier pharmaceutical and biotech accounts in Basel and Zurich, focusing on digital clinical trials and commercial transformation.", "timestamp": 24},
                {"speaker": "User", "text": "Understood. My current non-compete allows this sector directly. Please send over the confidential brief.", "timestamp": 42}
            ],
            "totalTurns": 4,
            "status": "Lead Captured",
            "createdAt": sub_mins(134)
        },
        {
            "id": "call_seed_003",
            "sessionId": "sess_oxane_jeffery_11902",
            "date": (now - datetime.timedelta(minutes=320)).strftime("%Y-%m-%d"),
            "time": "15:15:20",
            "startedAt": sub_mins(320),
            "endedAt": sub_mins(316),
            "durationSecs": 245.0,
            "durationFormatted": "4m 05s",
            "ipAddress": "68.195.89.201",
            "geoLocation": {
                "ip": "68.195.89.201",
                "city": "New York",
                "region": "New York",
                "country": "United States",
                "countryCode": "US",
                "timezone": "America/New_York",
                "isLocal": False
            },
            "agentId": "jeffery-oxane",
            "agentName": "Sara (Oxane Mandate)",
            "mandate": "Head of Sales US (Oxane Partners)",
            "route": "/talktosara-jeffery",
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) Mobile/15E148",
            "deviceType": "Mobile",
            "candidateInfo": {
                "name": "Jeffery Reiss",
                "email": "jeffery.reiss@privatecapital.com",
                "phone": "+1 (212) 555-0192",
                "currentRole": "Managing Director – FinTech & Private Markets",
                "notes": "Discussed North American institutional sales quota ($12M ARR). Follow up requested with London managing partner."
            },
            "segments": [
                {"speaker": "Assistant", "text": "Welcome Jeffery. I am Sara from TRANSEARCH International. We are conducting the confidential retained search for Oxane Partners for their Head of Sales US appointment.", "timestamp": 1},
                {"speaker": "User", "text": "Hi Sara. Yes, I am interested in how Oxane is positioning their credit valuation software against BlackRock Aladdin and legacy providers.", "timestamp": 12},
                {"speaker": "Assistant", "text": "Oxane specializes deeply in private debt portfolio monitoring and structured credit servicing, offering high-touch bespoke financial engineering alongside their SaaS stack.", "timestamp": 29}
            ],
            "totalTurns": 3,
            "status": "Completed",
            "createdAt": sub_mins(316)
        }
    ]

def init_db():
    """Initialize MongoDB connection, collections, indexes and seed data."""
    global client, db, interactions_col, users_col, is_mongo_connected, IN_MEMORY_STORE, IN_MEMORY_USERS

    print(f"[MongoDB] Connecting to {MONGODB_URI} (Database: {DB_NAME})...")
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2500)
        client.admin.command('ping')
        db = client[DB_NAME]
        interactions_col = db["interactions"]
        users_col = db["users"]

        # Ensure interaction indexes
        interactions_col.create_index([("id", ASCENDING)], unique=True)
        interactions_col.create_index([("sessionId", ASCENDING)])
        interactions_col.create_index([("startedAt", DESCENDING)])
        interactions_col.create_index([("agentId", ASCENDING)])
        interactions_col.create_index([("status", ASCENDING)])

        # Ensure user indexes
        users_col.create_index([("username", ASCENDING)], unique=True)

        # Seed calls data if empty
        if interactions_col.count_documents({}) == 0:
            initial = get_initial_seed_data()
            interactions_col.insert_many(initial)
            print(f"[MongoDB] Successfully seeded {len(initial)} initial call interactions.")

        # Seed default admin user in MongoDB if not exists
        admin_doc = users_col.find_one({"username": DEFAULT_ADMIN_USER.lower()})
        if not admin_doc:
            pwd_hash, salt = hash_password(DEFAULT_ADMIN_PASS)
            users_col.insert_one({
                "id": "user_root_admin",
                "username": DEFAULT_ADMIN_USER.lower(),
                "email": DEFAULT_ADMIN_USER.lower(),
                "role": "superadmin",
                "passwordHash": pwd_hash,
                "salt": salt,
                "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
            print(f"[MongoDB] Default admin user initialized: {DEFAULT_ADMIN_USER}")

        is_mongo_connected = True
        print("[MongoDB] Connected successfully and collections initialized!")
    except (ConnectionFailure, ServerSelectionTimeoutError) as err:
        is_mongo_connected = False
        print(f"[MongoDB Warning] Could not connect to MongoDB server at {MONGODB_URI}: {err}")
        print("[MongoDB Notice] Operating with memory store. To connect to MongoDB:")
        print("  1. Ensure MongoDB service is running: `mongod`")
        print("  2. Or set MONGODB_URI=<your_mongodb_atlas_url> in backend/.env")
        if not IN_MEMORY_STORE:
            IN_MEMORY_STORE = get_initial_seed_data()
        if not IN_MEMORY_USERS:
            pwd_hash, salt = hash_password(DEFAULT_ADMIN_PASS)
            IN_MEMORY_USERS.append({
                "id": "user_root_admin",
                "username": DEFAULT_ADMIN_USER.lower(),
                "email": DEFAULT_ADMIN_USER.lower(),
                "role": "superadmin",
                "passwordHash": pwd_hash,
                "salt": salt,
                "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })

# -------------------------------------------------------------
# User Account Management (MongoDB / Memory)
# -------------------------------------------------------------
def create_user(username: str, email: Optional[str], password: str, role: str = "consultant") -> Dict[str, Any]:
    """Create a new user account in MongoDB."""
    global is_mongo_connected, users_col, IN_MEMORY_USERS

    norm_user = username.strip().lower()
    norm_email = email.strip().lower() if email else norm_user
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    user_id = f"user_{int(datetime.datetime.now().timestamp() * 1000)}_{os.urandom(3).hex()}"

    pwd_hash, salt = hash_password(password)

    user_doc = {
        "id": user_id,
        "username": norm_user,
        "email": norm_email,
        "role": role,
        "passwordHash": pwd_hash,
        "salt": salt,
        "createdAt": now_iso
    }

    if is_mongo_connected and users_col is not None:
        if users_col.find_one({"username": norm_user}):
            raise ValueError(f"Account with username '{username}' already exists.")
        users_col.insert_one(user_doc)
    else:
        for u in IN_MEMORY_USERS:
            if u["username"] == norm_user:
                raise ValueError(f"Account with username '{username}' already exists.")
        IN_MEMORY_USERS.append(user_doc)

    print(f"👤 [User Management] Created account: {norm_user} ({role})")

    return {
        "id": user_id,
        "username": norm_user,
        "email": norm_email,
        "role": role,
        "createdAt": now_iso
    }

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record."""
    global is_mongo_connected, users_col, IN_MEMORY_USERS
    norm_user = username.strip().lower()

    if is_mongo_connected and users_col is not None:
        try:
            return users_col.find_one({"username": norm_user}, {"_id": 0})
        except Exception:
            pass

    for u in IN_MEMORY_USERS:
        if u["username"] == norm_user:
            return u
    return None

def verify_user_credentials(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Verify credentials against MongoDB users collection or default admin credentials."""
    norm_user = username.strip().lower()

    # 1. Check MongoDB database user
    user = get_user_by_username(norm_user)
    if user and "passwordHash" in user and "salt" in user:
        if verify_password(password, user["passwordHash"], user["salt"]):
            return {
                "id": user.get("id"),
                "username": user["username"],
                "email": user.get("email"),
                "role": user.get("role", "consultant")
            }

    # 2. Check default env credentials
    is_root_user = norm_user == DEFAULT_ADMIN_USER.lower() or norm_user == "admin"
    is_root_pass = password == DEFAULT_ADMIN_PASS
    if is_root_user and is_root_pass:
        return {
            "id": "user_root_admin",
            "username": DEFAULT_ADMIN_USER.lower(),
            "email": DEFAULT_ADMIN_USER.lower(),
            "role": "superadmin"
        }

    return None

def get_all_users() -> List[Dict[str, Any]]:
    """List all accounts without sensitive password hashes."""
    global is_mongo_connected, users_col, IN_MEMORY_USERS
    users_list = []

    if is_mongo_connected and users_col is not None:
        try:
            cursor = users_col.find({}, {"_id": 0, "passwordHash": 0, "salt": 0}).sort("createdAt", DESCENDING)
            users_list = list(cursor)
        except Exception as e:
            print(f"[MongoDB Error] User query failed: {e}")

    if not users_list:
        users_list = [
            {k: v for k, v in u.items() if k not in ("passwordHash", "salt")}
            for u in IN_MEMORY_USERS
        ]

    # Ensure root admin is present in list if empty
    if not any(u.get("username") in (DEFAULT_ADMIN_USER.lower(), "admin") for u in users_list):
        users_list.insert(0, {
            "id": "user_root_admin",
            "username": DEFAULT_ADMIN_USER.lower(),
            "email": DEFAULT_ADMIN_USER.lower(),
            "role": "superadmin",
            "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })

    return users_list

def delete_user(username: str) -> bool:
    """Delete a user account by username."""
    global is_mongo_connected, users_col, IN_MEMORY_USERS
    norm_user = username.strip().lower()

    # Prevent deleting primary root admin
    if norm_user in (DEFAULT_ADMIN_USER.lower(), "admin", "admin@transearch.com"):
        raise ValueError("Cannot delete the primary root superadmin account.")

    deleted = False
    if is_mongo_connected and users_col is not None:
        try:
            res = users_col.delete_one({"username": norm_user})
            deleted = res.deleted_count > 0
        except Exception as e:
            print(f"[MongoDB Error] User delete failed: {e}")

    prev_len = len(IN_MEMORY_USERS)
    IN_MEMORY_USERS = [u for u in IN_MEMORY_USERS if u.get("username") != norm_user]
    if len(IN_MEMORY_USERS) < prev_len:
        deleted = True

    if deleted:
        print(f"🗑️ [User Management] Deleted account: {norm_user}")

    return deleted

# -------------------------------------------------------------
# Interaction Calls Management (MongoDB / Memory)
# -------------------------------------------------------------
def save_interaction(interaction_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Save or update interaction in MongoDB or memory fallback."""
    global is_mongo_connected, interactions_col, IN_MEMORY_STORE

    call_id = interaction_dict.get("id")
    session_id = interaction_dict.get("sessionId")

    if is_mongo_connected and interactions_col is not None:
        try:
            filter_query = {"$or": [{"id": call_id}]}
            if session_id:
                filter_query["$or"].append({"sessionId": session_id})
            
            interactions_col.update_one(
                filter_query,
                {"$set": interaction_dict},
                upsert=True
            )
            return interaction_dict
        except Exception as e:
            print(f"[MongoDB Error] Failed to write to MongoDB, falling back: {e}")

    # Fallback in memory
    for i, item in enumerate(IN_MEMORY_STORE):
        if item.get("id") == call_id or (session_id and item.get("sessionId") == session_id):
            IN_MEMORY_STORE[i] = interaction_dict
            return interaction_dict
    
    IN_MEMORY_STORE.insert(0, interaction_dict)
    return interaction_dict

def get_all_interactions(
    agent_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    search_query: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Retrieve interactions with search and filters."""
    global is_mongo_connected, interactions_col, IN_MEMORY_STORE

    if is_mongo_connected and interactions_col is not None:
        try:
            query: Dict[str, Any] = {}

            if agent_filter and agent_filter != "all":
                query["$or"] = [
                    {"agentId": agent_filter},
                    {"agentName": {"$regex": agent_filter, "$options": "i"}}
                ]

            if status_filter and status_filter != "all":
                query["status"] = status_filter

            if search_query:
                s = search_query.strip()
                search_or = [
                    {"candidateInfo.name": {"$regex": s, "$options": "i"}},
                    {"candidateInfo.email": {"$regex": s, "$options": "i"}},
                    {"candidateInfo.phone": {"$regex": s, "$options": "i"}},
                    {"candidateInfo.notes": {"$regex": s, "$options": "i"}},
                    {"ipAddress": {"$regex": s, "$options": "i"}},
                    {"geoLocation.city": {"$regex": s, "$options": "i"}},
                    {"geoLocation.country": {"$regex": s, "$options": "i"}},
                    {"agentName": {"$regex": s, "$options": "i"}},
                    {"mandate": {"$regex": s, "$options": "i"}},
                    {"segments.text": {"$regex": s, "$options": "i"}}
                ]
                if "$or" in query:
                    query = {"$and": [{"$or": query["$or"]}, {"$or": search_or}]}
                else:
                    query["$or"] = search_or

            cursor = interactions_col.find(query, {"_id": 0}).sort("startedAt", DESCENDING).skip(skip).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"[MongoDB Error] Query failed: {e}")

    # Memory fallback
    results = list(IN_MEMORY_STORE)
    if agent_filter and agent_filter != "all":
        results = [r for r in results if r.get("agentId") == agent_filter or agent_filter.lower() in r.get("agentName", "").lower()]
    if status_filter and status_filter != "all":
        results = [r for r in results if r.get("status") == status_filter]
    if search_query:
        sq = search_query.lower()
        def matches(r):
            cand = r.get("candidateInfo") or {}
            c_name = cand.get("name", "").lower()
            c_email = cand.get("email", "").lower()
            c_notes = cand.get("notes", "").lower()
            ip = r.get("ipAddress", "").lower()
            city = (r.get("geoLocation") or {}).get("city", "").lower()
            country = (r.get("geoLocation") or {}).get("country", "").lower()
            agent = r.get("agentName", "").lower()
            mandate = r.get("mandate", "").lower()
            transcript = " ".join([seg.get("text", "").lower() for seg in r.get("segments", [])])
            return (sq in c_name or sq in c_email or sq in c_notes or sq in ip or sq in city or sq in country or sq in agent or sq in mandate or sq in transcript)
        results = [r for r in results if matches(r)]

    results.sort(key=lambda x: x.get("startedAt", ""), reverse=True)
    return results[skip:skip+limit]

def get_interaction_by_id(call_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve single interaction."""
    global is_mongo_connected, interactions_col, IN_MEMORY_STORE

    if is_mongo_connected and interactions_col is not None:
        try:
            doc = interactions_col.find_one({"$or": [{"id": call_id}, {"sessionId": call_id}]}, {"_id": 0})
            if doc:
                return doc
        except Exception as e:
            print(f"[MongoDB Error] Find failed: {e}")

    for item in IN_MEMORY_STORE:
        if item.get("id") == call_id or item.get("sessionId") == call_id:
            return item
    return None

def delete_interaction(call_id: str) -> bool:
    """Delete an interaction."""
    global is_mongo_connected, interactions_col, IN_MEMORY_STORE

    deleted = False
    if is_mongo_connected and interactions_col is not None:
        try:
            res = interactions_col.delete_one({"$or": [{"id": call_id}, {"sessionId": call_id}]})
            deleted = res.deleted_count > 0
        except Exception as e:
            print(f"[MongoDB Error] Delete failed: {e}")

    prev_len = len(IN_MEMORY_STORE)
    IN_MEMORY_STORE = [i for i in IN_MEMORY_STORE if i.get("id") != call_id and i.get("sessionId") != call_id]
    if len(IN_MEMORY_STORE) < prev_len:
        deleted = True

    return deleted

def compute_stats() -> Dict[str, Any]:
    """Calculate aggregate statistics."""
    calls = get_all_interactions(limit=1000)

    total_secs = sum(c.get("durationSecs", 0.0) for c in calls)
    leads_count = sum(
        1 for c in calls
        if c.get("status") == "Lead Captured" or
        bool((c.get("candidateInfo") or {}).get("name") or (c.get("candidateInfo") or {}).get("email"))
    )

    locations = set()
    agent_counts: Dict[str, int] = {}

    for c in calls:
        geo = c.get("geoLocation") or {}
        loc = geo.get("country") or geo.get("city")
        if loc:
            locations.add(loc)
        
        agent = c.get("agentName") or c.get("agentId") or "Unknown"
        agent_counts[agent] = agent_counts.get(agent, 0) + 1

    from geo_service import format_duration
    top_agents = [{"agentName": k, "count": v} for k, v in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

    return {
        "totalCalls": len(calls),
        "totalDurationSecs": total_secs,
        "totalDurationFormatted": format_duration(total_secs),
        "totalLeadsCaptured": leads_count,
        "uniqueLocationsCount": len(locations),
        "topAgents": top_agents,
        "mongoConnected": is_mongo_connected
    }
