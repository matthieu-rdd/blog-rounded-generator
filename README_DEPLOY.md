# Déploiement sur Streamlit Cloud

## Étapes rapides

1. **Pousser votre code sur GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push
   ```

2. **Aller sur https://share.streamlit.io/**

3. **Se connecter avec GitHub**

4. **Créer une nouvelle app**
   - Repository : votre repo GitHub
   - Branch : main (ou master)
   - Main file : `app.py`

5. **Configurer les secrets** (dans Advanced settings)
   - `OPENAI_API_KEY`
   - `PERPLEXITY_API_KEY`
   - `SANITY_PROJECT_ID`
   - `SANITY_DATASET`
   - `SANITY_TOKEN`

6. **Déployer !**

Votre app sera disponible sur : `https://votre-app-name.streamlit.app`

## Structure requise

Assurez-vous que ces fichiers sont présents :
- ✅ `app.py` (fichier principal)
- ✅ `requirements.txt` (dépendances)
- ✅ `.streamlit/config.toml` (configuration)
- ✅ `scripts/` (dossier avec les scripts)
- ✅ `utils/` (dossier avec les utilitaires)
- ✅ `data/` (dossier avec les fichiers JSON)

## Variables d'environnement

Toutes les variables doivent être configurées dans les "Secrets" de Streamlit Cloud :
- `OPENAI_API_KEY`
- `PERPLEXITY_API_KEY`
- `SANITY_PROJECT_ID`
- `SANITY_DATASET`
- `SANITY_TOKEN`
- `REVALIDATE_URL` (optionnel)

