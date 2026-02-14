"""Comprehensive smoke test for all routes (public + admin + WhatsApp)."""

from app import app, db, csrf


def main():
    app.config["WTF_CSRF_ENABLED"] = False
    c = app.test_client()

    # --- Public routes ---
    routes = ["/", "/about", "/services", "/portfolio", "/contact", "/health"]
    print("=== PUBLIC ROUTES ===")
    for r in routes:
        resp = c.get(r)
        status = resp.status_code
        ok = "OK" if status == 200 else f"FAIL({status})"
        print(f"  GET {r:30s} {ok}")

    # --- Admin routes (should redirect to login when unauthenticated) ---
    admin_routes = [
        "/admin/dashboard",
        "/admin/services",
        "/admin/portfolio",
        "/admin/advertisements",
        "/admin/users",
    ]
    print()
    print("=== ADMIN ROUTES (unauthenticated -> 302) ===")
    for r in admin_routes:
        resp = c.get(r)
        status = resp.status_code
        ok = "OK" if status == 302 else f"FAIL({status})"
        print(f"  GET {r:45s} {ok}")

    # --- Admin login ---
    print()
    print("=== ADMIN LOGIN ===")
    resp = c.get("/admin/login")
    print(f"  GET  /admin/login  status={resp.status_code}")

    resp = c.post(
        "/admin/login",
        data={"username": "admin", "password": "Admin@2024"},
        follow_redirects=False,
    )
    loc = resp.headers.get("Location", "none")[:60]
    print(f"  POST /admin/login  status={resp.status_code} location={loc}")

    # --- Admin pages while logged in ---
    print()
    print("=== ADMIN ROUTES (authenticated) ===")
    admin_pages = [
        "/admin/dashboard",
        "/admin/services",
        "/admin/portfolio",
        "/admin/advertisements",
        "/admin/users",
        "/admin/service/add",
        "/admin/portfolio/add",
        "/admin/advertisement/add",
        "/admin/change-password",
    ]
    for r in admin_pages:
        resp = c.get(r)
        status = resp.status_code
        ok = "OK" if status == 200 else f"FAIL({status})"
        print(f"  GET {r:45s} {ok}")

    # --- Forgot password (accessible without login) ---
    c2 = app.test_client()
    resp = c2.get("/admin/forgot-password")
    ok = "OK" if resp.status_code == 200 else f"FAIL({resp.status_code})"
    print(f"  GET /admin/forgot-password (no auth)             {ok}")

    # --- WhatsApp contact redirect ---
    print()
    print("=== WHATSAPP CONTACT ===")
    resp = c.post(
        "/contact",
        data={
            "name": "Test",
            "email": "test@test.com",
            "phone": "0881234567",
            "subject": "Test",
            "message": "Hello",
            "service_interest": "data",
            "inquiry_type": "quote",
        },
    )
    loc = resp.headers.get("Location", "none")[:70]
    ok = (
        "OK"
        if resp.status_code == 302 and "wa.me" in loc
        else f"FAIL({resp.status_code})"
    )
    print(f"  POST /contact -> WhatsApp  {ok}  location={loc}")

    print()
    print("=== ALL DONE ===")


if __name__ == "__main__":
    main()
