from main import app, UserModel


def test_get_users():
    with app.test_client() as client:
        response = client.get('/users')
        assert response.status_code == 200
        data = response.get_json()
        assert type(data) is list
        with app.app_context():
            count = UserModel.query.count()
            assert count == 28


def test_post_user():
    with app.test_client() as client:
        response = client.post(
            '/users', json={"first_name": "test_name", "last_name": "test_last_name"})
        assert response.status_code == 201
        data = response.get_json()
        assert data['first_name'] == 'test_name' and data['last_name'] == 'test_last_name' and data['parent1_id'] == None and data['parent2_id'] == None
        with app.app_context():
            count = UserModel.query.count()
            assert count == 29


def test_patch_user():
    with app.test_client() as client:
        response = client.patch(
            '/users/28', json={"last_name": "test_last_name"})
        assert response.status_code == 200
        data = response.get_json()
        assert data['first_name'] == 'Alice' and data['last_name'] == 'test_last_name' and data['parent1_id'] == 17 and data['parent2_id'] == None


def test_delete_user():
    with app.test_client() as client:
        response = client.delete('/users/2')
        assert response.status_code == 204
        with app.app_context():
            count = UserModel.query.count()
            users = UserModel.query.filter_by(id=28)
            print(users)
            assert count == 27


def test_tree():
    with app.test_client() as client:
        response = client.get('/tree/1')
        assert response.status_code == 200
        data = response.get_json()
        assert 'tree' in data
        assert data['tree']['id'] == 1
        assert data['max_node_depth'] == 4
