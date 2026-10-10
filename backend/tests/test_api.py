def test_registration_and_duplicate(client):
    payload = {"name":"Ada Lovelace","email":"ada@example.com","password":"password123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 409

def test_login_and_me(client):
    client.post("/api/auth/register", json={"name":"Ada Lovelace","email":"ada@example.com","password":"password123"})
    assert client.post("/api/auth/login", json={"email":"ada@example.com","password":"wrongpass"}).status_code == 401
    token = client.post("/api/auth/login", json={"email":"ada@example.com","password":"password123"}).json()["access_token"]
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200

def test_project_ownership(client, auth_headers):
    response = client.post("/api/projects", headers=auth_headers, json={"name":"Demo","repository_url":"https://github.com/org/repo"})
    assert response.status_code == 201
    project_id = response.json()["id"]
    assert client.get(f"/api/projects/{project_id}", headers=auth_headers).status_code == 200
    assert client.delete(f"/api/projects/{project_id}", headers=auth_headers).status_code == 204

def test_invalid_build_project(client, auth_headers):
    assert client.post("/api/projects/999/builds", headers=auth_headers).status_code == 404

def test_deploy_requires_successful_build(client, auth_headers):
    project = client.post("/api/projects", headers=auth_headers, json={"name":"Demo"}).json()
    response = client.post(f"/api/projects/{project['id']}/deploy", headers=auth_headers, json={"build_id": 1})
    assert response.status_code in (400, 404)
