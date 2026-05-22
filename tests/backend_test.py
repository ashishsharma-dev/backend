"""Serene Canvas backend API regression tests."""
import os
import uuid
import io
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001").rstrip("/")
API = f"{BASE_URL}/api"
ADMIN_EMAIL = "admin@website.com"
ADMIN_PASSWORD = "Admin@777"


def gif_bytes(width, height):
    header = b"GIF89a"
    logical_screen = width.to_bytes(2, "little") + height.to_bytes(2, "little") + b"\x80\x00\x00"
    color_table = b"\x00\x00\x00\xff\xff\xff"
    image_descriptor = b"\x2c\x00\x00\x00\x00" + width.to_bytes(2, "little") + height.to_bytes(2, "little") + b"\x00"
    image_data = b"\x02\x02D\x01\x00"
    trailer = b"\x3b"
    return header + logical_screen + color_table + image_descriptor + image_data + trailer


@pytest.fixture(scope="session")
def session():
    return requests.Session()


@pytest.fixture(scope="session")
def admin_session():
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=30)
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="session")
def sample_slug(session):
    r = session.get(f"{API}/posts", params={"limit": 1}, timeout=30)
    assert r.status_code == 200
    items = r.json().get("items", [])
    assert items, "No posts seeded"
    return items[0]["slug"]


# ---- Health & public ----
def test_root(session):
    r = session.get(f"{API}/", timeout=20)
    assert r.status_code == 200
    assert r.json().get("ok") is True


def test_categories(session):
    r = session.get(f"{API}/categories", timeout=20)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 6
    for c in data:
        assert "slug" in c and "count" in c


def test_categories_includes_cors_header(session):
    r = session.get(
        f"{API}/categories",
        headers={"Origin": "http://localhost:3000"},
        timeout=20,
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_posts_default_limit(session):
    r = session.get(f"{API}/posts", timeout=20)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 60
    assert len(data["items"]) == 12
    assert "content" not in data["items"][0]


def test_posts_filter_category(session):
    r = session.get(f"{API}/posts", params={"category": "tech", "limit": 20}, timeout=20)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 10
    assert all(p["category"] == "tech" for p in data["items"])


def test_posts_search(session):
    r = session.get(f"{API}/posts", params={"search": "the"}, timeout=20)
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_post_detail_and_views(session, sample_slug):
    r1 = session.get(f"{API}/posts/{sample_slug}", timeout=20)
    assert r1.status_code == 200
    p1 = r1.json()
    assert p1["slug"] == sample_slug
    assert "content" in p1 and p1["content"]
    assert isinstance(p1.get("related"), list)
    assert len(p1["related"]) <= 3
    v1 = p1["views"]
    r2 = session.get(f"{API}/posts/{sample_slug}", timeout=20)
    assert r2.json()["views"] == v1 + 1


def test_post_detail_404(session):
    r = session.get(f"{API}/posts/does-not-exist-xyz", timeout=20)
    assert r.status_code == 404


# ---- Comments ----
def test_comment_create_and_list(session, sample_slug):
    payload = {"name": "TEST_User", "email": "TEST_u@example.com", "content": "Great post!"}
    r = session.post(f"{API}/posts/{sample_slug}/comments", json=payload, timeout=20)
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "TEST_User"
    assert "email" not in data  # sanitized
    assert data["content"] == "Great post!"
    # list
    r2 = session.get(f"{API}/posts/{sample_slug}/comments", timeout=20)
    assert r2.status_code == 200
    cs = r2.json()
    assert any(c["id"] == data["id"] for c in cs)
    for c in cs:
        assert "email" not in c


def test_comment_too_short(session, sample_slug):
    r = session.post(f"{API}/posts/{sample_slug}/comments",
                     json={"name": "x", "email": "x@x.com", "content": "a"}, timeout=20)
    assert r.status_code == 400


# ---- Reactions ----
def test_reaction_increments(session, sample_slug):
    r0 = session.get(f"{API}/posts/{sample_slug}", timeout=20)
    before = r0.json().get("reactions", {}).get("like", 0)
    r = session.post(f"{API}/posts/{sample_slug}/react", json={"type": "like"}, timeout=20)
    assert r.status_code == 200
    assert r.json().get("like", 0) == before + 1


def test_reaction_invalid(session, sample_slug):
    r = session.post(f"{API}/posts/{sample_slug}/react", json={"type": "bad"}, timeout=20)
    assert r.status_code == 422


# ---- Newsletter / Contact ----
def test_newsletter_and_dedupe(session):
    email = f"TEST_{uuid.uuid4().hex[:8]}@example.com"
    r1 = session.post(f"{API}/newsletter", json={"email": email}, timeout=20)
    assert r1.status_code == 200 and "Subscribed" in r1.json()["message"]
    r2 = session.post(f"{API}/newsletter", json={"email": email}, timeout=20)
    assert r2.status_code == 200 and "Already" in r2.json()["message"]


def test_contact(session):
    r = session.post(f"{API}/contact", json={
        "name": "TEST_Q", "email": "TEST_q@example.com",
        "subject": "Hi", "message": "Hello team"
    }, timeout=20)
    assert r.status_code == 200 and r.json().get("ok") is True


# ---- Auth ----
def test_login_wrong(session):
    r = session.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": "wrong"}, timeout=20)
    assert r.status_code == 401


def test_login_sets_cookies():
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=20)
    assert r.status_code == 200
    assert "access_token" in s.cookies and "refresh_token" in s.cookies
    data = r.json()
    assert data["email"] == ADMIN_EMAIL and data["role"] == "admin"


def test_me_requires_auth(session):
    r = session.get(f"{API}/auth/me", timeout=20)
    assert r.status_code == 401


def test_auth_me_includes_cors_header_for_frontend_origin(session):
    r = session.get(
        f"{API}/auth/me",
        headers={"Origin": "http://localhost:3000"},
        timeout=20,
    )
    assert r.status_code == 401
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_me_with_auth(admin_session):
    r = admin_session.get(f"{API}/auth/me", timeout=20)
    assert r.status_code == 200
    assert r.json()["email"] == ADMIN_EMAIL


def test_logout_clears(admin_session):
    s = requests.Session()
    s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=20)
    r = s.post(f"{API}/auth/logout", timeout=20)
    assert r.status_code == 200
    r2 = s.get(f"{API}/auth/me", timeout=20)
    assert r2.status_code == 401


# ---- Admin protected ----
def test_admin_routes_unauth(session):
    for path in ["/admin/posts", "/admin/stats", "/admin/ads"]:
        r = session.get(f"{API}{path}", timeout=20)
        assert r.status_code == 401, f"{path} should be 401"
    r = session.post(f"{API}/admin/posts", json={"title": "x", "excerpt": "x", "content": "x", "category": "tech"}, timeout=20)
    assert r.status_code == 401
    r2 = session.post(f"{API}/admin/ads", json={"category": "tech", "image_url": "/media/ads/x.gif", "hyperlink": "https://example.com", "status": "active"}, timeout=20)
    assert r2.status_code == 401


def test_admin_stats(admin_session):
    r = admin_session.get(f"{API}/admin/stats", timeout=20)
    assert r.status_code == 200
    d = r.json()
    for k in ["total_posts", "published", "total_comments", "subscribers", "total_views"]:
        assert k in d
    assert d["total_posts"] >= 60


def test_admin_crud(admin_session):
    title = f"TEST_Post_{uuid.uuid4().hex[:6]}"
    payload = {"title": title, "excerpt": "exc", "content": "hello " * 50,
               "category": "tech", "tags": ["t"], "published": True}
    r = admin_session.post(f"{API}/admin/posts", json=payload, timeout=20)
    assert r.status_code == 200
    post = r.json()
    pid = post["id"]
    assert post["title"] == title
    # update
    r2 = admin_session.put(f"{API}/admin/posts/{pid}", json={"title": title + "_UP"}, timeout=20)
    assert r2.status_code == 200
    assert r2.json()["title"] == title + "_UP"
    # list
    r3 = admin_session.get(f"{API}/admin/posts", timeout=20)
    assert r3.status_code == 200
    assert any(p["id"] == pid for p in r3.json())
    # delete
    r4 = admin_session.delete(f"{API}/admin/posts/{pid}", timeout=20)
    assert r4.status_code == 200
    r5 = admin_session.put(f"{API}/admin/posts/{pid}", json={"title": "x"}, timeout=20)
    assert r5.status_code == 404


def test_ad_upload_validation_and_crud(admin_session):
    bad = admin_session.post(
        f"{API}/admin/ads/upload",
        files={"file": ("bad.gif", io.BytesIO(gif_bytes(300, 250)), "image/gif")},
        timeout=20,
    )
    assert bad.status_code == 400
    assert "728x90" in bad.json()["detail"].replace(" ", "")

    good = admin_session.post(
        f"{API}/admin/ads/upload",
        files={"file": ("good.gif", io.BytesIO(gif_bytes(728, 90)), "image/gif")},
        timeout=20,
    )
    assert good.status_code == 200
    upload = good.json()
    assert upload["image_url"].startswith("/media/ads/")

    create = admin_session.post(
        f"{API}/admin/ads",
        json={
            "category": "tech",
            "image_url": upload["image_url"],
            "hyperlink": "https://example.com/tech-ad",
            "status": "active",
        },
        timeout=20,
    )
    assert create.status_code == 200
    ad = create.json()
    assert ad["hyperlink"] == "https://example.com/tech-ad"
    assert ad["status"] == "active"

    public_active = admin_session.get(f"{API}/ads/placement", params={"category": "tech"}, timeout=20)
    assert public_active.status_code == 200
    assert public_active.json()["is_dummy"] is False
    assert public_active.json()["hyperlink"] == "https://example.com/tech-ad"

    paused = admin_session.put(f"{API}/admin/ads/{ad['id']}", json={"status": "paused"}, timeout=20)
    assert paused.status_code == 200
    assert paused.json()["status"] == "paused"

    public_paused = admin_session.get(f"{API}/ads/placement", params={"category": "tech"}, timeout=20)
    assert public_paused.status_code == 200
    assert public_paused.json()["is_dummy"] is True
    assert public_paused.json()["hyperlink"] is None

    deleted = admin_session.delete(f"{API}/admin/ads/{ad['id']}", timeout=20)
    assert deleted.status_code == 200


def test_ad_requires_hyperlink(admin_session):
    r = admin_session.post(
        f"{API}/admin/ads",
        json={"category": "sports", "image_url": "/media/ads/example.gif", "hyperlink": "", "status": "active"},
        timeout=20,
    )
    assert r.status_code == 422
