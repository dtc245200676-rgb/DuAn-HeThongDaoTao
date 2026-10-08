from app.models.user import User


def login_headers(client, email, password):
    r = client.post('/api/auth/login', json={'email': email, 'password': password})
    assert r.status_code == 200
    return {'Authorization': f"Bearer {r.json()['access_token']}"}


def test_s1_01_login_and_lock(client, user_factory):
    user_factory('teacher@example.com', 'Teacher123', 'teacher')
    ok = client.post('/api/auth/login', json={'email': 'teacher@example.com', 'password': 'Teacher123'})
    assert ok.status_code == 200 and ok.json()['role'] == 'teacher' and ok.json()['access_token']
    wrong = client.post('/api/auth/login', json={'email': 'teacher@example.com', 'password': 'wrongpass123'})
    missing = client.post('/api/auth/login', json={'email': 'missing@example.com', 'password': 'wrongpass123'})
    assert wrong.status_code == missing.status_code == 401
    assert wrong.json()['detail'] == missing.json()['detail'] == 'Email hoặc mật khẩu không đúng'
    user_factory('lock@example.com', 'Password123', 'student')
    for _ in range(5):
        assert client.post('/api/auth/login', json={'email': 'lock@example.com', 'password': 'wrong123'}).status_code == 401
    assert client.post('/api/auth/login', json={'email': 'lock@example.com', 'password': 'Password123'}).status_code == 423


def test_s1_02_session_refresh_logout(client, user_factory):
    user_factory('logout@example.com', 'Logout123', 'student')
    login = client.post('/api/auth/login', json={'email': 'logout@example.com', 'password': 'Logout123'})
    headers = {'Authorization': f"Bearer {login.json()['access_token']}"}
    assert client.get('/api/auth/me', headers=headers).status_code == 200
    assert client.post('/api/auth/refresh', headers=headers).status_code == 200
    assert client.post('/api/auth/logout', headers=headers).status_code == 200
    assert client.get('/api/auth/me', headers=headers).status_code == 401


def test_s1_03_reset_token_one_time_and_generic_response(client, user_factory, monkeypatch):
    user_factory('reset@example.com', 'OldPass123', 'student')
    monkeypatch.setattr('app.api.routes.auth_password_reset.generate_one_time_token', lambda: 'fixed-reset-token')
    existing = client.post('/api/auth/forgot-password', json={'email': 'reset@example.com'})
    missing = client.post('/api/auth/forgot-password', json={'email': 'notfound@example.com'})
    assert existing.status_code == missing.status_code == 200 and existing.json() == missing.json()
    assert client.post('/api/auth/reset-password', json={'token': 'fixed-reset-token', 'new_password': 'NewPass123'}).status_code == 200
    assert client.post('/api/auth/reset-password', json={'token': 'fixed-reset-token', 'new_password': 'Another123'}).status_code == 400


def test_s1_04_change_password_revokes_other_sessions(client, user_factory):
    user_factory('change@example.com', 'OldPass123', 'student')
    l1 = client.post('/api/auth/login', json={'email': 'change@example.com', 'password': 'OldPass123'})
    l2 = client.post('/api/auth/login', json={'email': 'change@example.com', 'password': 'OldPass123'})
    h1 = {'Authorization': f"Bearer {l1.json()['access_token']}"}
    h2 = {'Authorization': f"Bearer {l2.json()['access_token']}"}
    assert client.post('/api/auth/change-password', headers=h1, json={'current_password': 'wrong', 'new_password': 'Changed123'}).status_code == 400
    assert client.post('/api/auth/change-password', headers=h1, json={'current_password': 'OldPass123', 'new_password': 'Changed123'}).status_code == 200
    assert client.get('/api/auth/me', headers=h1).status_code == 200
    assert client.get('/api/auth/me', headers=h2).status_code == 401


def test_s1_05_rbac_three_roles(client, user_factory, admin_headers):
    user_factory('teacher2@example.com', 'Teacher123', 'teacher')
    user_factory('accountant@example.com', 'Account123', 'accountant')
    teacher = login_headers(client, 'teacher2@example.com', 'Teacher123')
    accountant = login_headers(client, 'accountant@example.com', 'Account123')
    assert client.get('/api/users', headers=admin_headers).status_code == 200
    assert client.get('/api/users', headers=teacher).status_code == 403
    assert client.get('/api/roles', headers=teacher).status_code == 403
    assert client.get('/api/roles', headers=accountant).status_code == 403
    assert 'tuition.edit' not in client.get('/api/auth/me', headers=teacher).json()['permissions']
    assert 'grades.edit' not in client.get('/api/auth/me', headers=accountant).json()['permissions']


def test_s1_08_create_activate_search_duplicate(client, admin_headers):
    created = client.post('/api/users', headers=admin_headers, json={'full_name': 'Nguyễn Văn A', 'email': 'nguyenvana@example.com', 'phone': '0901234567', 'role_slugs': ['teacher']})
    assert created.status_code == 200
    body = created.json()
    assert body['status'] == 'pending' and body['debug_temporary_password'] and body['debug_activation_token']
    activation = client.post('/api/auth/activate', json={'token': body['debug_activation_token'], 'temporary_password': body['debug_temporary_password']})
    assert activation.status_code == 200
    duplicate = client.post('/api/users', headers=admin_headers, json={'full_name': 'Nguyễn Văn B', 'email': 'nguyenvana@example.com', 'role_slugs': ['student']})
    assert duplicate.status_code == 409
    search = client.get('/api/users?q=0901234567&page=1&page_size=20', headers=admin_headers)
    assert search.status_code == 200 and search.json()['total'] == 1 and search.json()['page_size'] == 20


def test_s1_09_multi_role_effective_immediately_and_self_admin_protection(client, admin_headers, user_factory):
    target = user_factory('multi@example.com', 'Multi1234', 'teacher')
    target_headers = login_headers(client, 'multi@example.com', 'Multi1234')
    assert client.get('/api/users', headers=target_headers).status_code == 403
    assign = client.put(f'/api/users/{target.id}/roles', headers=admin_headers, json={'role_slugs': ['teacher', 'training_manager']})
    assert assign.status_code == 200
    assert {r['slug'] for r in assign.json()['roles']} == {'teacher', 'training_manager'}
    assert client.get('/api/users', headers=target_headers).status_code == 200
    me = client.get('/api/auth/me', headers=admin_headers).json()
    assert client.put(f"/api/users/{me['id']}/roles", headers=admin_headers, json={'role_slugs': ['teacher']}).status_code == 400


def test_s1_10_lock_unlock_revoke_session(client, admin_headers, user_factory):
    target = user_factory('lockeduser@example.com', 'User12345', 'teacher')
    target_headers = login_headers(client, 'lockeduser@example.com', 'User12345')
    locked = client.post(f'/api/users/{target.id}/lock', headers=admin_headers, json={'reason': 'Nhân sự đã nghỉ việc'})
    assert locked.status_code == 200
    assert locked.json()['user']['status'] == 'locked' and locked.json()['user']['needs_handover'] is True
    assert 'bàn giao' in locked.json()['handover_warning'].lower()
    assert client.get('/api/auth/me', headers=target_headers).status_code in (401, 403)
    assert client.post('/api/auth/login', json={'email': 'lockeduser@example.com', 'password': 'User12345'}).status_code == 403
    unlocked = client.post(f'/api/users/{target.id}/unlock', headers=admin_headers, json={'reason': 'Quay lại làm việc'})
    assert unlocked.status_code == 200 and unlocked.json()['user']['status'] == 'active'
