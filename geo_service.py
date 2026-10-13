import httpx
from typing import Optional, Dict
from fastapi import Request
from models import GeoLocation

IP_CACHE: Dict[str, GeoLocation] = {}

def get_client_ip(request: Request) -> str:
    """Extract client IP from request headers or socket."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Return first IP from comma-separated list
        ip = forwarded.split(",")[0].strip()
        if ip:
            return ip

    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    client_ip = request.headers.get("x-client-ip")
    if client_ip:
        return client_ip.strip()

    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"

def is_private_ip(ip: str) -> bool:
    """Check if IP is local/private network."""
    if not ip or ip in ("127.0.0.1", "::1", "localhost", "0.0.0.0"):
        return True
    if ip.startswith("10.") or ip.startswith("192.168."):
        return True
    if ip.startswith("172."):
        parts = ip.split(".")
        if len(parts) >= 2:
            try:
                second = int(parts[1])
                if 16 <= second <= 31:
                    return True
            except ValueError:
                pass
    if ip.startswith("fc00:") or ip.startswith("fd00:") or ip.startswith("fe80:"):
        return True
    return False

async def resolve_geo_location(ip: str, request: Optional[Request] = None) -> GeoLocation:
    """Resolve geolocation for an IP address."""
    if ip in IP_CACHE:
        return IP_CACHE[ip]

    # 1. Check platform headers (Vercel, Cloudflare, etc.)
    if request:
        vercel_country = request.headers.get("x-vercel-ip-country")
        vercel_city = request.headers.get("x-vercel-ip-city")
        vercel_region = request.headers.get("x-vercel-ip-country-region")
        cf_country = request.headers.get("cf-ipcountry")
        cf_city = request.headers.get("cf-ipcity")

        if vercel_country or cf_country:
            geo = GeoLocation(
                ip=ip,
                city=vercel_city or cf_city or "Regional Node",
                region=vercel_region,
                country=vercel_country or cf_country or "Global",
                countryCode=vercel_country or cf_country or "UN",
                isLocal=False,
            )
            IP_CACHE[ip] = geo
            return geo

    # 2. Localhost check
    if is_private_ip(ip):
        local_geo = GeoLocation(
            ip=ip,
            city="Localhost / Workstation",
            region="Development Lab",
            country="Local Network",
            countryCode="DEV",
            isLocal=True,
        )
        IP_CACHE[ip] = local_geo
        return local_geo

    # 3. Public IP lookup via ip-api with timeout
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            resp = await client.get(
                f"https://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,timezone"
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    geo = GeoLocation(
                        ip=ip,
                        city=data.get("city", "Unknown City"),
                        region=data.get("regionName"),
                        country=data.get("country", "Global"),
                        countryCode=data.get("countryCode", "UN"),
                        timezone=data.get("timezone"),
                        isLocal=False,
                    )
                    IP_CACHE[ip] = geo
                    return geo
    except Exception:
        pass

    # 4. Fallback
    fallback = GeoLocation(
        ip=ip,
        city="Direct Visitor",
        country="International",
        countryCode="GLOBAL",
        isLocal=False,
    )
    IP_CACHE[ip] = fallback
    return fallback

def get_device_type(user_agent: Optional[str]) -> str:
    """Detect device category from User-Agent string."""
    if not user_agent:
        return "Desktop"
    ua = user_agent.lower()
    if any(k in ua for k in ("tablet", "ipad", "playbook", "silk")):
        return "Tablet"
    if any(k in ua for k in ("mobile", "iphone", "android", "blackberry", "opera mini")):
        return "Mobile"
    return "Desktop"

def format_duration(seconds: float) -> str:
    """Format duration in seconds to '2m 15s' format."""
    if not seconds or seconds <= 0:
        return "0s"
    mins = int(seconds // 60)
    secs = int(round(seconds % 60))
    if mins == 0:
        return f"{secs}s"
    return f"{mins}m {secs:02d}s"
