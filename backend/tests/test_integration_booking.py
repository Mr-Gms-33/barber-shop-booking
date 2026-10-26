def test_booking_flow(client, db_session, next_weekday_10am):
    services = client.get("/api/services").json()
    assert len(services) >= 1
    service_id = services[0]["id"]
    barbers = client.get("/api/barbers").json()
    barber_id = barbers[0]["id"]

    payload = {
        "service_id": service_id,
        "start_at": next_weekday_10am.isoformat(),
        "barber_id": barber_id,
        "any_barber": False,
        "guest_name": "Test User",
        "guest_phone": "5551234567",
    }
    r = client.post("/api/bookings", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    code = data["booking"]["booking_code"]

    login = client.post(
        "/api/admin/login", json={"username": "admin", "password": "changeme"}
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    pending = client.get("/api/admin/appointments/pending", headers=headers).json()
    assert any(p["booking_code"] == code for p in pending)

    appt_id = next(p["id"] for p in pending if p["booking_code"] == code)
    acc = client.post(f"/api/admin/appointments/{appt_id}/accept", headers=headers, json={})
    assert acc.status_code == 200

    co = client.post(
        f"/api/admin/appointments/{appt_id}/checkout",
        headers=headers,
        json={"revenue": 22.5},
    )
    assert co.status_code == 200
