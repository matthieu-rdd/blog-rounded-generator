# Configuration n8n pour le Workflow Blog Sanity

Guide complet pour configurer votre workflow n8n avec les bonnes URLs et paramètres.

## URLs Sanity à utiliser

### Pour le dataset `development` (recommandé)

#### 1. Upload d'image (Upload Sanity Asset)
```
URL: https://8y6orojx.api.sanity.io/v2021-06-07/assets/images/development
Method: POST
Authentication: HTTP Bearer Auth
```

#### 2. Query des références (Fetch Sanity References)
```
URL: https://8y6orojx.api.sanity.io/v2021-06-07/data/query/development
Method: POST
Authentication: HTTP Bearer Auth
Content-Type: application/json
Body (JSON):
{
  "query": "{ \"category\": *[_type == \"category\" && slug.current == $categorySlug][0]._id, \"author\": *[_type == \"author\" && name == \"Matthieu HUBERT\"][0]._id }",
  "params": {
    "categorySlug": "={{ $('SEO Keyword Optimizer1').first().json.message.content.tag || '' }}"
  }
}
```

#### 3. Création du post (Create Sanity Post)
```
URL: https://8y6orojx.api.sanity.io/v2021-06-07/data/mutate/development
Method: POST
Authentication: HTTP Bearer Auth
Content-Type: application/json (ou raw)
Body: {{ $json.mutation }}
```

### Pour le dataset `production`

Remplacez simplement `development` par `production` dans toutes les URLs ci-dessus.

## Configuration des nodes n8n

### Node: Upload Sanity Asset
- **Type**: HTTP Request
- **Method**: POST
- **URL**: `https://8y6orojx.api.sanity.io/v2021-06-07/assets/images/development`
- **Authentication**: Generic Credential Type → HTTP Bearer Auth
- **Send Body**: Yes
- **Content Type**: Binary Data
- **Input Data Field Name**: `binary_file_data`

### Node: Fetch Sanity References
- **Type**: HTTP Request
- **Method**: POST
- **URL**: `https://8y6orojx.api.sanity.io/v2021-06-07/data/query/development`
- **Authentication**: Generic Credential Type → HTTP Bearer Auth
- **Send Body**: Yes
- **Body Content Type**: JSON
- **JSON Body**: 
```json
={{
  {
    "query": "{ \"category\": *[_type == \"category\" && slug.current == $categorySlug][0]._id, \"author\": *[_type == \"author\" && name == \"Matthieu HUBERT\"][0]._id }",
    "params": {
      "categorySlug": $('SEO Keyword Optimizer1').first().json.message.content.tag || ''
    }
  }
}}
```

### Node: Create Sanity Post
- **Type**: HTTP Request
- **Method**: POST
- **URL**: `https://8y6orojx.api.sanity.io/v2021-06-07/data/mutate/development`
- **Authentication**: Generic Credential Type → HTTP Bearer Auth
- **Send Body**: Yes
- **Body Content Type**: Raw
- **Body**: `={{ $json.mutation }}`

## Code JavaScript pour "Prepare Sanity Mutation"

```javascript
// Helper to generate unique keys
const generateKey = () => Math.random().toString(36).substring(7);

// Get IDs from Fetch Sanity References node
const queryResponse = $('Fetch Sanity References').first()?.json || {};
const refsData = queryResponse.result || queryResponse || {};
const categoryId = refsData.category || null;
const authorId = refsData.author || null;

// Build references with _key for categories
const categoryRef = categoryId ? {
  _key: generateKey(),
  _type: 'reference',
  _ref: categoryId
} : null;

const authorRef = authorId ? {
  _type: 'reference',
  _ref: authorId
} : null;

// Get body content as plain text
const bodyContent = $('SEO Keyword Optimizer1').first().json.message.content.blog_post || '';
if (!bodyContent || bodyContent.trim() === '') {
  throw new Error('Body content is empty or null');
}

// Get image asset ID from uploaded asset
const imageAssetId = $('Upload Sanity Asset').first().json.document._id;

// Build the mutation - ensure all required fields are strings, not null
const title = $('SEO Keyword Optimizer1').first().json.message.content.title || '';
const slug = $('SEO Keyword Optimizer1').first().json.message.content.slug || '';
const excerpt = $('SEO Keyword Optimizer1').first().json.message.content.summary || '';

if (!title || !slug) {
  throw new Error('Title or slug is missing');
}

// IMPORTANT: Pour créer un DRAFT, préfixez l'ID avec "drafts."
const baseId = slug.replace(/-/g, '_');
const documentId = `drafts.${baseId}`; // ← Préfixe "drafts." pour créer un brouillon

const postData = {
  _id: documentId, // ← ID avec préfixe drafts.
  _type: 'post',
  title: String(title),
  slug: {
    _type: 'slug',
    current: String(slug)
  },
  excerpt: String(excerpt),
  body: [{
    _key: generateKey(),
    _type: 'block',
    style: 'normal',
    children: [{
      _key: generateKey(),
      _type: 'span',
      text: bodyContent,
      marks: []
    }],
    markDefs: []
  }],
  publishedAt: new Date().toISOString()
};

if (imageAssetId) {
  postData.mainImage = {
    _type: 'image',
    asset: {
      _type: 'reference',
      _ref: imageAssetId
    }
  };
}

if (authorRef) {
  postData.author = authorRef;
}

if (categoryRef) {
  postData.categories = [categoryRef];
}

const mutation = {
  mutations: [{
    create: postData
  }]
};

return { json: { mutation: JSON.stringify(mutation) } };
```

## Pour créer en PRODUCTION (pas en brouillon)

Si vous voulez créer directement en production sans préfixe `drafts.`, modifiez cette ligne dans le code :

```javascript
// Pour production (pas de préfixe drafts.)
const documentId = baseId; // Sans préfixe "drafts."

// Au lieu de :
// const documentId = `drafts.${baseId}`;
```

## Variables d'environnement n8n (optionnel)

Si vous utilisez des variables d'environnement dans n8n, vous pouvez configurer :

```
SANITY_PROJECT_ID=8y6orojx
SANITY_DATASET=development
SANITY_USE_DRAFT=true
```

Et utiliser dans les URLs :
```
https://{{ $env.SANITY_PROJECT_ID }}.api.sanity.io/v2021-06-07/assets/images/{{ $env.SANITY_DATASET }}
```

## Points importants

1. ✅ **Pas d'endpoint `/draft`** : Utilisez toujours le dataset (`development` ou `production`)
2. ✅ **Drafts via ID** : Les brouillons sont créés en préfixant l'ID avec `drafts.`
3. ✅ **Même endpoint pour drafts et production** : L'URL reste identique, seule l'ID change
4. ✅ **Images** : Les assets sont uploadés normalement, sans préfixe drafts

## Checklist de configuration

- [ ] Token Sanity configuré avec les bonnes permissions
- [ ] URLs mises à jour (pas de `/draft` dans l'URL)
- [ ] Code JavaScript modifié pour ajouter `_id: "drafts.xxx"` dans la mutation
- [ ] Dataset configuré (`development` ou `production`)
- [ ] Authentication HTTP Bearer Auth configurée sur tous les nodes HTTP Request


