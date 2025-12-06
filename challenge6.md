## Challenge 6 – JWT revoked token

- **Nom :** JWT revoked token  
- **URL :** https://www.root-me.org/fr/Challenges/Web-Serveur/JWT-Jeton-revoque

### Étapes de découverte

1. Ouverture du challenge Root-Me.
2. Appel de l'endpoint `/login` avec le payload suivant pour s'authentifier en tant qu'`admin` :

   ```json
   {
       "username": "admin",
       "password": "admin"
   }
   ```

   Récupération du token JWT dans la réponse.
   ![img.png](/images/challenge6/getAccessToken.png)

3. Appel de l'endpoint `/admin` avec le token JWT récupéré :

   ```text
   GET /web-serveur/ch63/admin HTTP/1.1
   Host: challenge01.root-me.org
   Authorization: Bearer <token>
   ```

   Récupération du message "Token is revoked" dans la réponse.
   ![img.png](/images/challenge6/tokenRevoked.png)

4. Contournement de la revocation du token, ajout d'un = à la fin du token 

   le = est un caractère valide pour un token JWT, il est donc possible de contourner la revocation du token en ajoutant un = à la fin du token. on peut voir aussi dans la source code que le token est stocké dans un set et que le set est verrouillé par un lock, donc il est possible de contourner la revocation du token en ajoutant un = à la fin du token.
   
   ```text
   GET /web-serveur/ch63/admin HTTP/1.1
   Host: challenge01.root-me.org
   Authorization: Bearer <token>=
   ```

    Récupération du flag dans la réponse.
    ![img.png](/images/challenge6/flag.png)

### Les recommandations

Pour éviter ce type de contournement, il est recommandé de :

1. **Comparer l'identifiant unique du token (JTI) plutôt que le token brut** : Au lieu de stocker et comparer le token JWT complet dans la blacklist, il faut utiliser le claim `jti` (JWT ID) qui est un identifiant unique du token. Cela permet d'éviter les contournements basés sur l'ajout de caractères supplémentaires comme le "=".

   **Source :** [OWASP JWT Security Cheat Sheet - Token Revocation](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html#token-revocation)

2. **Décoder et normaliser le token avant comparaison** : Si l'utilisation du `jti` n'est pas possible, il faut décoder le token JWT avant de le comparer avec la blacklist, puis comparer les tokens décodés normalisés plutôt que les chaînes brutes.

   **Source :** [OWASP JWT Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

3. **Utiliser un identifiant dérivé du token** : Une autre approche consiste à créer un hash ou un identifiant unique basé sur le contenu décodé du token (par exemple, un hash des claims principaux) plutôt que de stocker le token brut.

   **Source :** [OWASP JWT Security Cheat Sheet - Token Revocation](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html#token-revocation)

Ces approches garantissent que la vérification de révocation ne peut pas être contournée par des modifications superficielles du token comme l'ajout de caractères padding.
