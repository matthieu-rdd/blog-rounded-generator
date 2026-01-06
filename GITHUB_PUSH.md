# Guide pour pousser le code sur GitHub

## Problème actuel

Le push échoue avec une erreur 403 (Permission denied). Cela signifie que :
- Soit le token n'a pas les bonnes permissions
- Soit le token a expiré
- Soit le compte utilisé n'a pas accès au repository

## Solution : Créer un nouveau token avec les bonnes permissions

### Étape 1 : Créer un token GitHub

1. Allez sur https://github.com/settings/tokens
2. Cliquez sur **"Generate new token"** → **"Generate new token (classic)"**
3. Donnez-lui un nom : `blog-generator-push`
4. **IMPORTANT** : Cochez la scope **`repo`** (accès complet aux repositories)
5. Cliquez sur **"Generate token"**
6. **Copiez le token immédiatement** (il ne sera affiché qu'une fois !)

### Étape 2 : Utiliser le token

Une fois que vous avez le nouveau token, exécutez ces commandes :

```bash
# Remplacez VOTRE_NOUVEAU_TOKEN par le token que vous venez de créer
git remote set-url origin https://VOTRE_NOUVEAU_TOKEN@github.com/matthieu-rdd/blog-rounded-generator.git
git push -u origin main
```

## Alternative : Utiliser GitHub Desktop

Si vous avez GitHub Desktop installé :

1. Ouvrez GitHub Desktop
2. File → Add Local Repository
3. Sélectionnez le dossier : `/Users/julespoirette/test - blog - rdd`
4. Cliquez sur "Publish repository" ou "Push origin"

## Alternative : Upload via l'interface web

1. Allez sur https://github.com/matthieu-rdd/blog-rounded-generator
2. Cliquez sur "uploading an existing file"
3. Glissez-déposez tous les fichiers du projet

## Vérification

Une fois le push réussi, vous devriez voir vos fichiers sur :
https://github.com/matthieu-rdd/blog-rounded-generator

## Commits prêts à être poussés

Vous avez actuellement 3 commits locaux qui ne sont pas sur GitHub :
- `3e41967` - Improve login page centering and reduce spacing
- `fb3c991` - Simplify authentication and add Rounded branding to sidebar  
- `8e3543b` - Add API keys documentation and deployment summary

