"""Serene Canvas — Blog API. FastAPI + MongoDB. JWT admin auth, anonymous comments/reactions."""
from dotenv import load_dotenv
from pathlib import Path
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

import os
import logging
import uuid
import bcrypt
import jwt
import re
import struct
from urllib.parse import quote
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response, Query, UploadFile, File
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr, HttpUrl

from seed_data import get_seed_posts, CATEGORIES_META, slugify

# ---------- Setup ----------
JWT_ALGORITHM = "HS256"

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="Githy API")
api = APIRouter(prefix="/api")
MEDIA_DIR = ROOT_DIR / "media"
ADS_DIR = MEDIA_DIR / "ads"
POST_COVERS_DIR = MEDIA_DIR / "post-covers"
LEADERBOARD_WIDTH = 728
LEADERBOARD_HEIGHT = 90
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
ADS_DIR.mkdir(parents=True, exist_ok=True)
POST_COVERS_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Helpers ----------
def env_flag(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_csv(name: str, default: str = "") -> List[str]:
    raw = os.environ.get(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def normalize_cors_origins(origins: List[str]) -> tuple[List[str], Optional[str]]:
    cleaned = []
    for origin in origins:
        value = origin.rstrip("/")
        if value and value not in cleaned:
            cleaned.append(value)

    if not cleaned:
        cleaned = ["http://localhost:3000", "http://127.0.0.1:3000"]

    if "*" in cleaned:
        return [], ".*"

    return cleaned, None


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def jwt_secret() -> str:
    return os.environ["JWT_SECRET"]


def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email,
               "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
               "type": "access"}
    return jwt.encode(payload, jwt_secret(), algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id,
               "exp": datetime.now(timezone.utc) + timedelta(days=7),
               "type": "refresh"}
    return jwt.encode(payload, jwt_secret(), algorithm=JWT_ALGORITHM)


def cookie_settings() -> dict:
    same_site = os.environ.get("COOKIE_SAMESITE", "lax").strip().lower()
    if same_site not in {"lax", "strict", "none"}:
        same_site = "lax"
    return {
        "httponly": True,
        "secure": env_flag("COOKIE_SECURE", False),
        "samesite": same_site,
        "max_age": 3600,
        "path": "/",
    }


def refresh_cookie_settings() -> dict:
    settings = cookie_settings()
    settings["max_age"] = 604800
    return settings


def set_auth_cookies(response: Response, access: str, refresh: str):
    response.set_cookie("access_token", access, **cookie_settings())
    response.set_cookie("refresh_token", refresh, **refresh_cookie_settings())


def get_image_dimensions(data: bytes) -> tuple[Optional[int], Optional[int]]:
    if len(data) < 10:
        return None, None

    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        width, height = struct.unpack(">II", data[16:24])
        return width, height

    if data[:6] in {b"GIF87a", b"GIF89a"} and len(data) >= 10:
        width, height = struct.unpack("<HH", data[6:10])
        return width, height

    if data.startswith(b"RIFF") and data[8:12] == b"WEBP" and len(data) >= 30:
        if data[12:16] == b"VP8X":
            width = 1 + int.from_bytes(data[24:27], "little")
            height = 1 + int.from_bytes(data[27:30], "little")
            return width, height
        if data[12:16] == b"VP8 " and len(data) >= 30:
            width, height = struct.unpack("<HH", data[26:30])
            return width & 0x3FFF, height & 0x3FFF
        if data[12:16] == b"VP8L" and len(data) >= 25:
            bits = int.from_bytes(data[21:25], "little")
            width = (bits & 0x3FFF) + 1
            height = ((bits >> 14) & 0x3FFF) + 1
            return width, height

    if data.startswith(b"\xff\xd8"):
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            i += 2
            if marker in {0xD8, 0xD9}:
                continue
            if i + 2 > len(data):
                break
            segment_length = struct.unpack(">H", data[i:i + 2])[0]
            if segment_length < 2 or i + segment_length > len(data):
                break
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                height, width = struct.unpack(">HH", data[i + 3:i + 7])
                return width, height
            i += segment_length

    return None, None


def detect_extension(data: bytes, content_type: str) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n") or content_type == "image/png":
        return ".png"
    if data[:6] in {b"GIF87a", b"GIF89a"} or content_type == "image/gif":
        return ".gif"
    if data.startswith(b"\xff\xd8") or content_type in {"image/jpeg", "image/jpg"}:
        return ".jpg"
    if (data.startswith(b"RIFF") and data[8:12] == b"WEBP") or content_type == "image/webp":
        return ".webp"
    return ""


def build_dummy_ad(category: Optional[str] = None) -> dict:
    category_label = (category or "Sponsored").strip().title()
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{LEADERBOARD_WIDTH}" height="{LEADERBOARD_HEIGHT}" viewBox="0 0 {LEADERBOARD_WIDTH} {LEADERBOARD_HEIGHT}">
      <defs>
        <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#f7f1e6" />
          <stop offset="100%" stop-color="#ece2d4" />
        </linearGradient>
      </defs>
      <rect width="100%" height="100%" fill="url(#g)" rx="8" ry="8" />
      <rect x="12" y="12" width="704" height="66" fill="none" stroke="#839788" stroke-width="1.5" stroke-dasharray="7 5" rx="6" ry="6" />
      <text x="28" y="38" fill="#2f4f4f" font-size="15" font-family="Georgia, serif">Placeholder Advertisement</text>
      <text x="28" y="61" fill="#5c6b6d" font-size="12" font-family="Arial, sans-serif">{category_label} placement is currently unavailable</text>
    </svg>
    """.strip()
    return {
        "id": "dummy-ad",
        "category": category,
        "image_url": f"data:image/svg+xml;utf8,{quote(re.sub(r'\\s+', ' ', svg))}",
        "hyperlink": None,
        "status": "paused",
        "is_dummy": True,
    }


async def get_public_ad_for_category(category: Optional[str], request: Optional[Request] = None) -> dict:
    if category:
        latest_for_category = await db.ads.find_one(
            {"category": category},
            {"_id": 0},
            sort=[("updated_at", -1), ("created_at", -1)],
        )
        if not latest_for_category:
            return build_dummy_ad(category)
        if latest_for_category.get("status") != "active":
            return build_dummy_ad(category)
        ad = latest_for_category
    else:
        ad = await db.ads.find_one({"status": "active"}, {"_id": 0}, sort=[("updated_at", -1), ("created_at", -1)])

    if not ad:
        return build_dummy_ad(category)

    ad["is_dummy"] = False
    if request and ad.get("image_url", "").startswith("/media/"):
        ad["image_url"] = str(request.base_url).rstrip("/") + ad["image_url"]
    return ad


async def get_current_admin(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = jwt.decode(token, jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(401, "Invalid token type")
        user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0})
        if not user:
            raise HTTPException(401, "User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")


# ---------- Models ----------
class LoginIn(BaseModel):
    email: EmailStr
    password: str


class PostIn(BaseModel):
    title: str
    excerpt: str
    content: str
    category: str
    author: str = "Editorial Team"
    cover_image: str = ""
    tags: List[str] = []
    published: bool = True


class PostUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    cover_image: Optional[str] = None
    tags: Optional[List[str]] = None
    published: Optional[bool] = None


class CommentIn(BaseModel):
    name: str
    email: EmailStr
    content: str


class ReactionIn(BaseModel):
    type: str = Field(pattern="^(like|love|insightful)$")


class NewsletterIn(BaseModel):
    email: EmailStr


class ContactIn(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


class AdIn(BaseModel):
    category: str
    image_url: str
    hyperlink: HttpUrl
    status: str = Field(pattern="^(active|paused)$")


class AdUpdate(BaseModel):
    category: Optional[str] = None
    image_url: Optional[str] = None
    hyperlink: Optional[HttpUrl] = None
    status: Optional[str] = Field(default=None, pattern="^(active|paused)$")


# ---------- Auth ----------
@api.post("/auth/login")
async def login(payload: LoginIn, response: Response):
    email = payload.email.lower()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    access = create_access_token(user["id"], user["email"])
    refresh = create_refresh_token(user["id"])
    set_auth_cookies(response, access, refresh)
    return {"id": user["id"], "email": user["email"], "name": user.get("name", "Admin"), "role": user.get("role", "admin")}


@api.get("/auth/me")
async def me(user: dict = Depends(get_current_admin)):
    return user


@api.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"ok": True}


@api.post("/auth/refresh")
async def refresh(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(401, "No refresh token")
    try:
        payload = jwt.decode(token, jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Invalid token type")
        user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0})
        if not user:
            raise HTTPException(401, "User not found")
        access = create_access_token(user["id"], user["email"])
        response.set_cookie("access_token", access, **cookie_settings())
        return {"ok": True}
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid refresh token")


# ---------- Public Posts ----------
def _strip(p: dict) -> dict:
    p.pop("_id", None)
    return p


@api.get("/categories")
async def list_categories():
    counts = {c["slug"]: 0 for c in CATEGORIES_META}
    pipeline = [{"$match": {"published": True}}, {"$group": {"_id": "$category", "n": {"$sum": 1}}}]
    async for row in db.posts.aggregate(pipeline):
        counts[row["_id"]] = row["n"]
    return [{**c, "count": counts.get(c["slug"], 0)} for c in CATEGORIES_META]


@api.get("/ads/placement")
async def get_ad_placement(request: Request, category: Optional[str] = None):
    return await get_public_ad_for_category(category, request)


@api.get("/posts")
async def list_posts(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(12, ge=1, le=60),
    skip: int = Query(0, ge=0),
    featured: Optional[bool] = None,
):
    q: Dict = {"published": True}
    if category:
        q["category"] = category
    if search:
        q["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"excerpt": {"$regex": search, "$options": "i"}},
        ]
    cursor = db.posts.find(q, {"_id": 0, "content": 0}).sort("published_at", -1).skip(skip).limit(limit)
    items = await cursor.to_list(limit)
    total = await db.posts.count_documents(q)
    return {"items": items, "total": total}


@api.get("/posts/{slug}")
async def get_post(slug: str):
    post = await db.posts.find_one({"slug": slug, "published": True}, {"_id": 0})
    if not post:
        raise HTTPException(404, "Post not found")
    await db.posts.update_one({"slug": slug}, {"$inc": {"views": 1}})
    post["views"] = post.get("views", 0) + 1
    # related
    related_cursor = db.posts.find(
        {"category": post["category"], "slug": {"$ne": slug}, "published": True},
        {"_id": 0, "content": 0},
    ).sort("published_at", -1).limit(3)
    post["related"] = await related_cursor.to_list(3)
    return post


@api.post("/posts/{slug}/comments")
async def add_comment(slug: str, payload: CommentIn):
    post = await db.posts.find_one({"slug": slug}, {"_id": 0, "id": 1})
    if not post:
        raise HTTPException(404, "Post not found")
    if len(payload.content.strip()) < 2:
        raise HTTPException(400, "Comment too short")
    doc = {
        "id": str(uuid.uuid4()),
        "post_slug": slug,
        "name": payload.name.strip()[:80],
        "email": payload.email.lower(),
        "content": payload.content.strip()[:2000],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "approved": True,
    }
    await db.comments.insert_one(doc)
    doc.pop("_id", None)
    doc.pop("email", None)
    return doc


@api.get("/posts/{slug}/comments")
async def list_comments(slug: str):
    cursor = db.comments.find({"post_slug": slug, "approved": True}, {"_id": 0, "email": 0}).sort("created_at", -1)
    return await cursor.to_list(200)


@api.post("/posts/{slug}/react")
async def react(slug: str, payload: ReactionIn):
    post = await db.posts.find_one({"slug": slug}, {"_id": 0})
    if not post:
        raise HTTPException(404, "Post not found")
    field = f"reactions.{payload.type}"
    await db.posts.update_one({"slug": slug}, {"$inc": {field: 1}})
    updated = await db.posts.find_one({"slug": slug}, {"_id": 0, "reactions": 1})
    return updated.get("reactions", {})


@api.post("/newsletter")
async def newsletter(payload: NewsletterIn):
    existing = await db.newsletter.find_one({"email": payload.email.lower()})
    if existing:
        return {"ok": True, "message": "Already subscribed"}
    await db.newsletter.insert_one({
        "id": str(uuid.uuid4()),
        "email": payload.email.lower(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"ok": True, "message": "Subscribed"}


@api.post("/contact")
async def contact(payload: ContactIn):
    await db.contacts.insert_one({
        "id": str(uuid.uuid4()),
        "name": payload.name,
        "email": payload.email.lower(),
        "subject": payload.subject,
        "message": payload.message,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"ok": True}


# ---------- Admin ----------
@api.get("/admin/posts")
async def admin_list_posts(_: dict = Depends(get_current_admin)):
    cursor = db.posts.find({}, {"_id": 0}).sort("published_at", -1)
    return await cursor.to_list(500)


@api.post("/admin/posts")
async def admin_create_post(payload: PostIn, _: dict = Depends(get_current_admin)):
    now = datetime.now(timezone.utc).isoformat()
    slug = slugify(payload.title)
    if await db.posts.find_one({"slug": slug}):
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"
    doc = {
        "id": str(uuid.uuid4()),
        "slug": slug,
        **payload.model_dump(),
        "published_at": now,
        "created_at": now,
        "updated_at": now,
        "views": 0,
        "reactions": {"like": 0, "love": 0, "insightful": 0},
        "read_time": max(3, len(payload.content.split()) // 200),
    }
    await db.posts.insert_one(doc)
    doc.pop("_id", None)
    return doc


@api.post("/admin/posts/upload-cover")
async def admin_upload_post_cover(file: UploadFile = File(...), _: dict = Depends(get_current_admin)):
    content = await file.read()
    extension = detect_extension(content, file.content_type or "")
    if not extension:
        raise HTTPException(400, "Unsupported image format. Please upload PNG, JPG, GIF, or WebP.")

    POST_COVERS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extension}"
    target = POST_COVERS_DIR / filename
    target.write_bytes(content)
    return {"image_url": f"/media/post-covers/{filename}"}


@api.put("/admin/posts/{post_id}")
async def admin_update_post(post_id: str, payload: PostUpdate, _: dict = Depends(get_current_admin)):
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "No fields to update")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.posts.update_one({"id": post_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(404, "Post not found")
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    return post


@api.delete("/admin/posts/{post_id}")
async def admin_delete_post(post_id: str, _: dict = Depends(get_current_admin)):
    result = await db.posts.delete_one({"id": post_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Post not found")
    return {"ok": True}


@api.get("/admin/stats")
async def admin_stats(_: dict = Depends(get_current_admin)):
    total_posts = await db.posts.count_documents({})
    published = await db.posts.count_documents({"published": True})
    total_comments = await db.comments.count_documents({})
    total_subs = await db.newsletter.count_documents({})
    pipeline = [{"$group": {"_id": None, "total_views": {"$sum": "$views"}}}]
    views_doc = await db.posts.aggregate(pipeline).to_list(1)
    total_views = views_doc[0]["total_views"] if views_doc else 0
    return {
        "total_posts": total_posts,
        "published": published,
        "total_comments": total_comments,
        "subscribers": total_subs,
        "total_views": total_views,
    }


@api.get("/admin/contacts")
async def admin_contacts(_: dict = Depends(get_current_admin)):
    cursor = db.contacts.find({}, {"_id": 0}).sort("created_at", -1).limit(200)
    return await cursor.to_list(200)


@api.get("/admin/ads")
async def admin_list_ads(_: dict = Depends(get_current_admin)):
    cursor = db.ads.find({}, {"_id": 0}).sort("updated_at", -1)
    return await cursor.to_list(500)


@api.post("/admin/ads/upload")
async def admin_upload_ad_creative(file: UploadFile = File(...), _: dict = Depends(get_current_admin)):
    content = await file.read()
    width, height = get_image_dimensions(content)
    if (width, height) != (LEADERBOARD_WIDTH, LEADERBOARD_HEIGHT):
        raise HTTPException(400, f"Creative must be exactly {LEADERBOARD_WIDTH}x{LEADERBOARD_HEIGHT}px")

    extension = detect_extension(content, file.content_type or "")
    if not extension:
        raise HTTPException(400, "Unsupported image format. Please upload PNG, JPG, GIF, or WebP.")

    ADS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extension}"
    target = ADS_DIR / filename
    target.write_bytes(content)
    return {"image_url": f"/media/ads/{filename}", "width": width, "height": height}


@api.post("/admin/ads")
async def admin_create_ad(payload: AdIn, _: dict = Depends(get_current_admin)):
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": str(uuid.uuid4()),
        "category": payload.category,
        "image_url": payload.image_url.strip(),
        "hyperlink": str(payload.hyperlink).strip(),
        "status": payload.status,
        "created_at": now,
        "updated_at": now,
    }
    await db.ads.insert_one(doc)
    doc.pop("_id", None)
    return doc


@api.put("/admin/ads/{ad_id}")
async def admin_update_ad(ad_id: str, payload: AdUpdate, _: dict = Depends(get_current_admin)):
    updates = {k: (str(v).strip() if k == "hyperlink" and v is not None else v) for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "No fields to update")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.ads.update_one({"id": ad_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(404, "Ad not found")
    ad = await db.ads.find_one({"id": ad_id}, {"_id": 0})
    return ad


@api.delete("/admin/ads/{ad_id}")
async def admin_delete_ad(ad_id: str, _: dict = Depends(get_current_admin)):
    result = await db.ads.delete_one({"id": ad_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Ad not found")
    return {"ok": True}


# ---------- Health ----------
@api.get("/")
async def root():
    return {"service": "global-trend-hub", "ok": True}


# ---------- Startup ----------
@app.on_event("startup")
async def startup():
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    ADS_DIR.mkdir(parents=True, exist_ok=True)
    POST_COVERS_DIR.mkdir(parents=True, exist_ok=True)
    await db.posts.create_index("slug", unique=True)
    await db.posts.create_index("category")
    await db.posts.create_index("published_at")
    await db.ads.create_index("category")
    await db.ads.create_index("status")
    await db.users.create_index("email", unique=True)
    await db.newsletter.create_index("email", unique=True)
    await db.comments.create_index("post_slug")

    # Seed admin
    admin_email = os.environ["ADMIN_EMAIL"].lower()
    admin_password = os.environ["ADMIN_PASSWORD"]
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": admin_email,
            "password_hash": hash_password(admin_password),
            "name": "Editor in Chief",
            "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one(
            {"email": admin_email},
            {"$set": {"password_hash": hash_password(admin_password)}},
        )

    # Seed posts
    count = await db.posts.count_documents({})
    if count == 0:
        seed = get_seed_posts()
        await db.posts.insert_many(seed)
        logging.info("Seeded %d posts", len(seed))


@app.on_event("shutdown")
async def shutdown():
    client.close()


app.include_router(api)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
default_cors_origins = "http://localhost:3000,http://127.0.0.1:3000"
cors_origins, allow_origin_regex = normalize_cors_origins(
    env_csv("CORS_ORIGINS", default_cors_origins)
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins,
    allow_origin_regex=allow_origin_regex,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
