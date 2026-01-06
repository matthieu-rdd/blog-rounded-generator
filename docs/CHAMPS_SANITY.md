# 📋 Champs Sanity Remplis Automatiquement

Le script `generate_article.py` remplit automatiquement tous les champs requis pour Sanity :

## ✅ Champs Remplis

### Informations de base
- ✅ **Language** : `fr` (Français)
- ✅ **Translation Group** : Identifiant basé sur le slug
- ✅ **Title** : Titre de l'article (généré par OpenAI)
- ✅ **Slug** : Slug URL-friendly (généré par OpenAI)
- ✅ **Author** : Référence à "Matthieu HUBERT" (récupérée depuis Sanity)
- ✅ **Published at** : Date/heure de publication

### Contenu
- ✅ **Body** : Contenu en format Sanity Block Content structuré (H2, H3, paragraphes, listes)
- ✅ **Excerpt** : Résumé court (155-160 caractères)

### SEO
- ✅ **Meta Title** : Titre SEO optimisé (50-60 caractères)
- ✅ **Meta Description** : Description SEO (155-160 caractères)
- ✅ **Canonical URL** : URL canonique (`https://callrounded.com/blog/{slug}`)

### Open Graph
- ✅ **OG Title** : Titre Open Graph
- ✅ **OG Description** : Description Open Graph (155-160 caractères)
- ✅ **OG Type** : `article`

### Autres
- ✅ **Categories** : Référence à la catégorie (basée sur le tag)
- ✅ **Robots** : Par défaut `{noindex: false, nofollow: false}` (indexable)

## ⚠️ Champs à Remplir Manuellement (optionnels)

- ⚠️ **Main image** : Image principale (pas encore géré automatiquement)
  - Texte alternatif
  - Légende
  
- ⚠️ **Tags** : Tags de l'article (peut être ajouté plus tard)

- ⚠️ **Robots** : Peut être modifié pour `noindex`/`nofollow` si nécessaire

## 🔄 Format Block Content

Le script convertit automatiquement le HTML en format Sanity Block Content :

- `<h2>` → Block avec `style: "h2"`
- `<h3>` → Block avec `style: "h3"`
- `<p>` → Block avec `style: "normal"`
- `<ul><li>` → Blocks avec `listItem: "bullet"`
- `<strong>` → Spans avec `marks: ["strong"]`

## 📝 Exemple de Structure

```json
{
  "_id": "tele_secretariat_medical_vs_agent_vocal",
  "_type": "post",
  "title": "Télésecrétariat médical vs Agent Vocal : lequel choisir en 2025 ?",
  "slug": {
    "_type": "slug",
    "current": "tele-secretariat-medical-vs-agent-vocal"
  },
  "excerpt": "...",
  "body": [
    {
      "_key": "...",
      "_type": "block",
      "style": "h2",
      "children": [...]
    },
    {
      "_key": "...",
      "_type": "block",
      "style": "normal",
      "children": [...]
    }
  ],
  "metaTitle": "...",
  "metaDescription": "...",
  "canonicalUrl": "https://callrounded.com/blog/tele-secretariat-medical-vs-agent-vocal",
  "translationGroup": "tele-secretariat-medical-vs-agent-vocal",
  "language": "fr",
  "ogTitle": "...",
  "ogDescription": "...",
  "ogType": "article",
  "robots": {
    "noindex": false,
    "nofollow": false
  },
  "author": {
    "_type": "reference",
    "_ref": "author-id"
  },
  "categories": [...],
  "publishedAt": "2025-11-03T17:13:00.000Z"
}
```

