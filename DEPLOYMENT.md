# Guide de Déploiement

## Option 1 : Streamlit Cloud (Recommandé - Gratuit)

Streamlit Cloud est la solution la plus simple pour déployer une application Streamlit.

### Étapes de déploiement :

1. **Pousser le code sur GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/votre-username/votre-repo.git
   git push -u origin main
   ```

2. **Créer un compte sur Streamlit Cloud**
   - Aller sur https://share.streamlit.io/
   - Se connecter avec votre compte GitHub

3. **Déployer l'application**
   - Cliquer sur "New app"
   - Sélectionner votre repository GitHub
   - Choisir la branche (généralement `main`)
   - Spécifier le fichier principal : `app.py`
   - Cliquer sur "Deploy"

4. **Configurer les variables d'environnement**
   Dans les paramètres de l'app sur Streamlit Cloud, ajouter :
   - `OPENAI_API_KEY`
   - `PERPLEXITY_API_KEY`
   - `SANITY_PROJECT_ID`
   - `SANITY_DATASET`
   - `SANITY_TOKEN`
   - `REVALIDATE_URL` (optionnel)

5. **Votre app sera disponible sur** : `https://votre-app.streamlit.app`

## Option 2 : Vercel (Nécessite conversion en Next.js)

Vercel ne supporte pas directement Streamlit. Pour utiliser Vercel, il faudrait :
1. Convertir l'application Streamlit en Next.js/React
2. Créer une API backend pour les fonctions Python
3. Utiliser des fonctions serverless pour les appels API

Cette conversion nécessiterait une refonte complète de l'application.

## Option 3 : Autres plateformes

### Railway
- Supporte Python/Streamlit nativement
- Gratuit avec limitations
- https://railway.app

### Render
- Supporte Streamlit
- Gratuit avec limitations
- https://render.com

### Heroku
- Supporte Streamlit
- Payant (plus de plan gratuit)
- https://heroku.com

## Variables d'environnement requises

Assurez-vous de configurer ces variables dans votre plateforme de déploiement :

```
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
SANITY_PROJECT_ID=8y6orojx
SANITY_DATASET=development
SANITY_TOKEN=...
REVALIDATE_URL=https://... (optionnel)
```

## Fichiers nécessaires pour le déploiement

- `app.py` : Application principale
- `requirements.txt` : Dépendances Python
- `.streamlit/config.toml` : Configuration Streamlit
- `scripts/` : Scripts de génération
- `utils/` : Utilitaires
- `data/` : Données (articles, keywords)

## Notes importantes

- Les fichiers dans `articles/` seront créés dynamiquement
- Le dossier `data/` doit être présent avec les fichiers JSON nécessaires
- Les variables d'environnement doivent être configurées sur la plateforme de déploiement

