# Guide de Dépannage - Déploiement Streamlit Cloud

## Problèmes courants et solutions

### 1. Erreur : "Module not found" ou "Import error"

**Solution :** Vérifiez que tous les fichiers nécessaires sont dans le repository :
- ✅ `app.py` (fichier principal)
- ✅ `requirements.txt` (dépendances)
- ✅ `scripts/generate_article.py`
- ✅ `utils/sanity_utils.py`
- ✅ `data/articles_existants.json`
- ✅ `data/keywords.json`

### 2. Erreur : "File not found" pour les fichiers JSON

**Solution :** Les fichiers dans `data/` doivent être présents. Vérifiez qu'ils sont bien commités :
```bash
git add data/
git commit -m "Add data files"
git push
```

### 3. Erreur : "API Key not found" ou variables d'environnement manquantes

**Solution :** Configurez les secrets dans Streamlit Cloud :
1. Allez sur https://share.streamlit.io/
2. Sélectionnez votre app
3. Settings → Secrets
4. Ajoutez toutes les variables :

```toml
OPENAI_API_KEY = "sk-..."
PERPLEXITY_API_KEY = "pplx-..."
SANITY_PROJECT_ID = "8y6orojx"
SANITY_DATASET = "development"
SANITY_TOKEN = "..."
```

### 4. Erreur : "Cannot import generate_article"

**Solution :** Vérifiez que le chemin d'import est correct dans `app.py`. Le code actuel devrait fonctionner.

### 5. L'app se charge mais ne fonctionne pas

**Vérifications :**
- ✅ Tous les secrets sont configurés
- ✅ Le fichier principal est bien `app.py`
- ✅ La branche est `main`
- ✅ Les logs dans Streamlit Cloud pour voir les erreurs

## Étapes de déploiement détaillées

### Étape 1 : Vérifier que tout est sur GitHub

```bash
# Vérifier que tous les fichiers sont commités
git status

# Si des fichiers manquent, les ajouter
git add .
git commit -m "Add missing files"
git push
```

### Étape 2 : Créer l'app sur Streamlit Cloud

1. Allez sur https://share.streamlit.io/
2. Cliquez sur "New app"
3. **Repository :** `matthieu-rdd/blog-rounded-generator`
4. **Branch :** `main`
5. **Main file path :** `app.py`
6. Cliquez sur "Deploy"

### Étape 3 : Configurer les secrets

Dans Settings → Secrets, ajoutez :

```toml
OPENAI_API_KEY = "sk-..."
PERPLEXITY_API_KEY = "pplx-..."
SANITY_PROJECT_ID = "8y6orojx"
SANITY_DATASET = "development"
SANITY_TOKEN = "..."
REVALIDATE_URL = "https://..." # Optionnel
```

### Étape 4 : Redémarrer l'app

Après avoir ajouté les secrets, redémarrez l'app depuis le dashboard.

## Vérification finale

Une fois déployé, votre app devrait être accessible sur :
`https://[nom-de-votre-app].streamlit.app`

## Logs et débogage

Pour voir les erreurs :
1. Allez sur le dashboard Streamlit Cloud
2. Cliquez sur "Manage app"
3. Allez dans l'onglet "Logs"
4. Vérifiez les erreurs affichées

## Problème spécifique ?

Décrivez l'erreur exacte que vous voyez et je pourrai vous aider à la résoudre.

