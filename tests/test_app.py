import pytest
from app.main import create_app
from app.models import db, Name, Match

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

def test_get_names(client):
    """Test getting a list of names."""
    response = client.get('/names')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    
    # Test filtering by gender
    response = client.get('/names?gender=Female')
    assert response.status_code == 200
    data = response.get_json()
    assert all(name['gender'] == 'Female' for name in data)
    
    # Test filtering by origin
    response = client.get('/names?origin=ES')
    assert response.status_code == 200
    data = response.get_json()
    assert all(name['origin'] == 'ES' for name in data)

def test_like_name(client):
    """Test liking a name."""
    # First get a name
    response = client.get('/names')
    names = response.get_json()
    name_id = names[0]['id']
    
    # Test liking a name as user 1
    response = client.post('/like', json={
        'name_id': name_id,
        'user_id': 1,
        'liked': True
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'matched' in data
    assert not data['matched']  # Should not match yet
    
    # Test liking the same name as user 2
    response = client.post('/like', json={
        'name_id': name_id,
        'user_id': 2,
        'liked': True
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['matched']  # Should match now

def test_get_matches(client):
    """Test getting matches."""
    # Create a match
    response = client.get('/names')
    names = response.get_json()
    name_id = names[0]['id']
    
    # Both users like the name
    client.post('/like', json={
        'name_id': name_id,
        'user_id': 1,
        'liked': True
    })
    client.post('/like', json={
        'name_id': name_id,
        'user_id': 2,
        'liked': True
    })
    
    # Get matches
    response = client.get('/matches')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['name'] == names[0]['name'] 