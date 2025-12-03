"""
Tests pour l'application XSS Comments
Ces tests vérifient que l'application fonctionne ET que la vulnérabilité XSS est présente
"""
import pytest
from app import app, comments


@pytest.fixture
def client():
    """Fixture pour créer un client de test Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # Nettoyer les commentaires après chaque test
    comments.clear()


def test_homepage_loads(client):
    """Test que la page d'accueil se charge correctement"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Livre d\'Or' in response.data or b'Commentaires' in response.data


def test_health_endpoint(client):
    """Test du endpoint health check"""
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'ok'
    assert 'comments_count' in json_data


def test_post_comment(client):
    """Test de la fonctionnalité d'ajout de commentaire"""
    response = client.post('/post', data={
        'author': 'TestUser',
        'text': 'Ceci est un commentaire de test'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'TestUser' in response.data
    assert b'Ceci est un commentaire de test' in response.data


def test_xss_vulnerability_present(client):
    """
    Test CRITIQUE: Vérifie que la vulnérabilité XSS est PRÉSENTE
    Ce test confirme que le script n'est PAS échappé (comportement attendu)
    """
    xss_payload = "<script>alert('XSS')</script>"

    response = client.post('/post', data={
        'author': 'Attacker',
        'text': xss_payload
    }, follow_redirects=True)

    assert response.status_code == 200

    # Vérifier que le payload est présent SANS échappement dans le commentaire
    # Le payload doit être trouvé après "Attacker" dans la section des commentaires
    assert xss_payload.encode() in response.data
    assert b'<strong>Attacker</strong>' in response.data

    # Vérifier qu'on peut trouver le script non-échappé dans le contexte du commentaire
    # En cherchant la séquence: Attacker ... <script>
    response_text = response.data.decode('utf-8')
    attacker_pos = response_text.find('<strong>Attacker</strong>')
    assert attacker_pos != -1
    # Le script non échappé doit apparaître après le nom de l'attaquant
    script_pos = response_text.find(xss_payload, attacker_pos)
    assert script_pos != -1


def test_multiple_comments(client):
    """Test avec plusieurs commentaires"""
    # Ajouter 3 commentaires
    for i in range(3):
        client.post('/post', data={
            'author': f'User{i}',
            'text': f'Comment {i}'
        })

    response = client.get('/')
    assert response.status_code == 200

    # Vérifier que tous les commentaires sont présents
    for i in range(3):
        assert f'User{i}'.encode() in response.data
        assert f'Comment {i}'.encode() in response.data


def test_clear_comments(client):
    """Test du nettoyage des commentaires"""
    # Ajouter un commentaire
    client.post('/post', data={
        'author': 'TestUser',
        'text': 'Test comment'
    })

    # Nettoyer
    response = client.get('/clear', follow_redirects=True)
    assert response.status_code == 200

    # Vérifier via health check
    health_response = client.get('/health')
    json_data = health_response.get_json()
    assert json_data['comments_count'] == 0


def test_empty_comment_not_posted(client):
    """Test qu'un commentaire vide n'est pas posté"""
    client.post('/post', data={
        'author': 'TestUser',
        'text': ''
    }, follow_redirects=True)

    health_response = client.get('/health')
    json_data = health_response.get_json()
    assert json_data['comments_count'] == 0


def test_xss_img_tag_vulnerability(client):
    """Test de la vulnérabilité XSS avec balise img"""
    xss_payload = '<img src=x onerror="alert(\'XSS\')">'

    response = client.post('/post', data={
        'author': 'Attacker2',
        'text': xss_payload
    }, follow_redirects=True)

    assert response.status_code == 200
    assert xss_payload.encode() in response.data


def test_comment_persistence(client):
    """Test que les commentaires persistent entre les requêtes"""
    # Ajouter un commentaire
    client.post('/post', data={
        'author': 'PersistUser',
        'text': 'Persistent comment'
    })

    # Faire une nouvelle requête
    response = client.get('/')
    assert b'PersistUser' in response.data
    assert b'Persistent comment' in response.data


def test_html_injection(client):
    """Test d'injection HTML brut"""
    html_payload = '<h1>Injected HTML</h1>'

    response = client.post('/post', data={
        'author': 'HTMLInjector',
        'text': html_payload
    }, follow_redirects=True)

    assert response.status_code == 200
    # Le HTML doit être injecté directement
    assert html_payload.encode() in response.data
