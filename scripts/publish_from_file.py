#!/usr/bin/env python3
"""
Script pour publier un article directement depuis un fichier de review
"""

import os
import sys
import json
import requests
import uuid
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Fonction de conversion locale

# Token Sanity
SANITY_TOKEN_ENV = os.getenv("SANITY_TOKEN", "")
SANITY_TOKEN = SANITY_TOKEN_ENV if SANITY_TOKEN_ENV else "skyTy1Xvie474Pt4OYYa7s0HqD1aGgCb7RZyxFOYJ9HBq15hHOPzMaI6BxPdhMnOi1yT0zQ3ubBlnVV7us72zp40zB5iN1mlCVbl7wUMux4EZveQkZlRyvqUs0rxKT1y9ahmoskzhphhzUYSKrA4DGtHMI3cCgtlVUTgyZkcz2P9OQa22mz2"
SANITY_PROJECT_ID = "8y6orojx"
SANITY_DATASET = "production"  # Changé de "development" à "production"
SANITY_API_URL = f"https://{SANITY_PROJECT_ID}.api.sanity.io/v2025-12-11"


def generate_key():
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def convert_text_to_sanity_blocks(text: str) -> list:
    """
    Convertit du texte brut (markdown-like) en format Sanity Block Content
    Amélioré pour mieux détecter les titres et sous-titres
    """
    blocks = []
    lines = text.split('\n')
    
    current_paragraph = []
    is_first_line = True  # Pour détecter le titre principal au début
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        if not line_stripped:
            # Ligne vide = fin de paragraphe
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                # IMPORTANT: Parser les marks (**texte**) même dans les paragraphes normaux
                children, mark_defs = parse_marks(para_text)
                blocks.append({
                    "_key": generate_key(),
                    "_type": "block",
                    "style": "normal",
                    "children": children,
                    "markDefs": mark_defs
                })
                current_paragraph = []
            is_first_line = False
            continue
        
        line = line_stripped
        
        # Titre principal au début du document (sans #)
        if is_first_line and i < 3 and not line.startswith('#') and not re.match(r'^\d+\.', line):
            # Vérifier si c'est un titre (ligne courte, pas trop longue)
            if len(line) < 100 and not line.endswith('.'):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    children, mark_defs = parse_marks(para_text)
                    blocks.append({
                        "_key": generate_key(),
                        "_type": "block",
                        "style": "normal",
                        "children": children,
                        "markDefs": mark_defs
                    })
                    current_paragraph = []
                title_text = line
                children, mark_defs = parse_marks(title_text)
                blocks.append({
                    "_key": generate_key(),
                    "_type": "block",
                    "style": "h2",
                    "children": children,
                    "markDefs": mark_defs
                })
                is_first_line = False
                continue
        
        # H1/H2 (commence par #)
        if line.startswith('# '):
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                children, mark_defs = parse_marks(para_text)
                blocks.append({
                    "_key": generate_key(),
                    "_type": "block",
                    "style": "normal",
                    "children": children,
                    "markDefs": mark_defs
                })
                current_paragraph = []
            title_text = line[2:].strip()
            children, mark_defs = parse_marks(title_text)
            blocks.append({
                "_key": generate_key(),
                "_type": "block",
                "style": "h2",
                "children": children,
                "markDefs": mark_defs
            })
            is_first_line = False
            continue
        
        # H2 (commence par ##)
        if line.startswith('## '):
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                children, mark_defs = parse_marks(para_text)
                blocks.append({
                    "_key": generate_key(),
                    "_type": "block",
                    "style": "normal",
                    "children": children,
                    "markDefs": mark_defs
                })
                current_paragraph = []
            title_text = line[3:].strip()
            children, mark_defs = parse_marks(title_text)
            blocks.append({
                "_key": generate_key(),
                "_type": "block",
                "style": "h2",
                "children": children,
                "markDefs": mark_defs
            })
            continue
        
        # H3 (commence par ###)
        if line.startswith('### '):
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                children, mark_defs = parse_marks(para_text)
                blocks.append({
                    "_key": generate_key(),
                    "_type": "block",
                    "style": "normal",
                    "children": children,
                    "markDefs": mark_defs
                })
                current_paragraph = []
            title_text = line[4:].strip()
            children, mark_defs = parse_marks(title_text)
            blocks.append({
                "_key": generate_key(),
                "_type": "block",
                "style": "h3",
                "children": children,
                "markDefs": mark_defs
            })
            continue
        
        # Détecter les titres de sections numérotées EN PREMIER (ex: "1. Titre" ou "2. Titre")
        # Important: avant de détecter les listes, car sinon ils sont traités comme des listes
        numbered_title_match = re.match(r'^(\d+)\.\s+(.+)$', line)
        if numbered_title_match:
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                children, mark_defs = parse_marks(para_text)
                blocks.append({
                    "_key": generate_key(),
                    "_type": "block",
                    "style": "normal",
                    "children": children,
                    "markDefs": mark_defs
                })
                current_paragraph = []
            # Traiter comme un H2 - CONSERVER LE NUMÉRO
            number = numbered_title_match.group(1)
            title_text = numbered_title_match.group(2).strip()
            # Reconstruire le titre avec le numéro : "1. Titre"
            full_title = f"{number}. {title_text}"
            children, mark_defs = parse_marks(full_title)
            blocks.append({
                "_key": generate_key(),
                "_type": "block",
                "style": "h2",
                "children": children,
                "markDefs": mark_defs
            })
            is_first_line = False
            continue
        
        # Liste à puces (commence par • ou - ou numéro comme "1. " MAIS pas un titre de section)
        # Les titres numérotés ont déjà été traités ci-dessus
        if line.startswith('• ') or line.startswith('- ') or (re.match(r'^\d+\.\s+', line) and len(line) < 60):
            # Si c'est un numéro mais que c'est court, c'est peut-être une liste dans une liste
            # Sinon c'est un titre de section déjà traité
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                children, mark_defs = parse_marks(para_text)
                blocks.append({
                    "_key": generate_key(),
                    "_type": "block",
                    "style": "normal",
                    "children": children,
                    "markDefs": mark_defs
                })
                current_paragraph = []
            
            # Enlever le préfixe (•, -, ou numéro)
            item_text = re.sub(r'^(•|-|\d+\.)\s*', '', line)
            # Traiter le gras **texte**
            children, mark_defs = parse_marks(item_text)
            
            blocks.append({
                "_key": generate_key(),
                "_type": "block",
                "style": "normal",
                "listItem": "bullet",
                "children": children,
                "markDefs": mark_defs
            })
            is_first_line = False
            continue
        
        # Détecter les titres de conclusion (commencent par "Conclusion :", "Conclusion:", etc.)
        conclusion_match = re.match(r'^Conclusion\s*:?\s*(.+)$', line, re.IGNORECASE)
        if conclusion_match:
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                children, mark_defs = parse_marks(para_text)
                blocks.append({
                    "_key": generate_key(),
                    "_type": "block",
                    "style": "normal",
                    "children": children,
                    "markDefs": mark_defs
                })
                current_paragraph = []
            # Traiter comme un H2
            conclusion_text = conclusion_match.group(1).strip()
            full_conclusion = f"Conclusion : {conclusion_text}"
            children, mark_defs = parse_marks(full_conclusion)
            blocks.append({
                "_key": generate_key(),
                "_type": "block",
                "style": "h2",
                "children": children,
                "markDefs": mark_defs
            })
            is_first_line = False
            continue
        
        # Détecter les sous-titres (H3) - lignes courtes sans ponctuation finale, suivies d'une ligne vide
        # Exemples: "Absorption des appels répétitifs", "Un système de décharge cognitive"
        # Conditions: 
        # - Ligne courte (< 80 caractères)
        # - Pas de point final (sauf si c'est une abréviation)
        # - Suivie d'une ligne vide (vérifier la prochaine ligne)
        # - Pas de numéro au début
        # - Commence par une majuscule
        is_next_line_empty = i + 1 < len(lines) and not lines[i + 1].strip()
        is_short_line = len(line) < 80
        has_no_final_period = not line.endswith('.')
        starts_with_capital = line and line[0].isupper()
        is_not_numbered = not re.match(r'^\d+\.', line)
        is_not_bullet = not line.startswith('•') and not line.startswith('-')
        is_not_conclusion = not re.match(r'^Conclusion\s*:', line, re.IGNORECASE)
        
        # Vérifier si c'est probablement un sous-titre (H3)
        if (is_next_line_empty and is_short_line and has_no_final_period and 
            starts_with_capital and is_not_numbered and is_not_bullet and is_not_conclusion and
            not line.startswith('#') and len(line.split()) < 10):
            # Vérifier que ce n'est pas le début d'une phrase (pas de majuscules partout)
            has_lowercase = any(c.islower() for c in line)
            
            if has_lowercase:  # C'est un sous-titre (mixte majuscules/minuscules)
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    children, mark_defs = parse_marks(para_text)
                    blocks.append({
                        "_key": generate_key(),
                        "_type": "block",
                        "style": "normal",
                        "children": children,
                        "markDefs": mark_defs
                    })
                    current_paragraph = []
                # Traiter comme un H3
                children, mark_defs = parse_marks(line)
                blocks.append({
                    "_key": generate_key(),
                    "_type": "block",
                    "style": "h3",
                    "children": children,
                    "markDefs": mark_defs
                })
                is_first_line = False
                continue
        
        # Texte normal
        current_paragraph.append(line)
        is_first_line = False
    
    # Ajouter le dernier paragraphe
    if current_paragraph:
        para_text = ' '.join(current_paragraph)
        # Convertir les liens au format "Découvrir Donna" en format markdown [texte](url)
        para_text = convert_plain_link_to_markdown(para_text)
        children, mark_defs = parse_marks(para_text)
        blocks.append({
            "_key": generate_key(),
            "_type": "block",
            "style": "normal",
            "children": children,
            "markDefs": mark_defs
        })
    
    # Si aucun bloc, créer un bloc vide
    if not blocks:
        blocks.append({
            "_key": generate_key(),
            "_type": "block",
            "style": "normal",
            "children": [{"_key": generate_key(), "_type": "span", "text": text, "marks": []}],
            "markDefs": []
        })
    
    return blocks


def convert_plain_link_to_markdown(text: str) -> str:
    """
    Convertit les liens au format '... : Découvrir Donna' en format markdown '[Découvrir Donna](url)'
    """
    url = "https://callrounded.com/cas-usage/secretariat-medical"
    
    # Pattern pour détecter ': Découvrir Donna' ou ': Discover Donna' sans lien existant
    pattern_fr = r':\s*(Découvrir\s+Donna)(?!.*\])'
    pattern_en = r':\s*(Discover\s+Donna)(?!.*\])'
    
    if re.search(pattern_fr, text):
        text = re.sub(pattern_fr, f': [Découvrir Donna]({url})', text)
    elif re.search(pattern_en, text):
        text = re.sub(pattern_en, f': [Discover Donna]({url})', text)
    
    return text


def parse_marks(text: str):
    """
    Parse le texte et extrait les marques :
    - Gras **texte**
    - Liens [texte](url) -> markDefs de type link
    Retourne (children, mark_defs)
    """
    children = []
    mark_defs = []

    if not text:
        return ([{
            "_key": generate_key(),
            "_type": "span",
            "text": "",
            "marks": []
        }], [])

    link_pattern = re.compile(r'\[([^\]]+)\]\((https?://[^\s)]+)\)')
    pos = 0

    def add_bold_segments(segment: str):
        # Ajoute les spans en gérant le gras **texte**
        bold_pattern = r'\*\*([^*]+?)\*\*'
        last = 0
        for m in re.finditer(bold_pattern, segment):
            if m.start() > last:
                normal = segment[last:m.start()]
                if normal:
                    children.append({
                        "_key": generate_key(),
                        "_type": "span",
                        "text": normal,
                        "marks": []
                    })
            bold_text = m.group(1)
            if bold_text:
                children.append({
                    "_key": generate_key(),
                    "_type": "span",
                    "text": bold_text,
                    "marks": ["strong"]
                })
            last = m.end()
        if last < len(segment):
            tail = segment[last:]
            if tail:
                children.append({
                    "_key": generate_key(),
                    "_type": "span",
                    "text": tail,
                    "marks": []
                })

    for match in link_pattern.finditer(text):
        # Avant le lien
        if match.start() > pos:
            add_bold_segments(text[pos:match.start()])

        link_text = match.group(1)
        link_url = match.group(2)
        mark_key = generate_key()
        mark_defs.append({
            "_key": mark_key,
            "_type": "link",
            "href": link_url
        })
        # Lien : supporte aussi le gras à l'intérieur
        bold_inside = re.match(r'\*\*(.+)\*\*$', link_text)
        if bold_inside:
            link_clean = bold_inside.group(1)
            children.append({
                "_key": generate_key(),
                "_type": "span",
                "text": link_clean,
                "marks": ["strong", mark_key]
            })
        else:
            children.append({
                "_key": generate_key(),
                "_type": "span",
                "text": link_text,
                "marks": [mark_key]
            })

        pos = match.end()

    # Après le dernier lien
    if pos < len(text):
        add_bold_segments(text[pos:])

    # Si aucun enfant, retour texte brut
    if not children:
        children.append({
            "_key": generate_key(),
            "_type": "span",
            "text": text,
            "marks": []
        })

    return children, mark_defs


def add_to_knowledge_base(title: str, slug: str):
    """Ajoute l'article à la base de connaissances"""
    json_path = Path(__file__).parent.parent / "data" / "articles_existants.json"
    
    try:
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
        else:
            articles = []
        
        # Vérifier si l'article existe déjà
        existing = any(art.get("titre") == title or art.get("slug") == slug for art in articles)
        if not existing:
            articles.insert(0, {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "auteur": "Matthieu HUBERT",
                "titre": title,
                "slug": slug,
                "description": ""
            })
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Article ajouté à la base de connaissances")
    except Exception as e:
        print(f"⚠️  Erreur lors de l'ajout à la base: {e}")


def parse_review_file(filepath: Path) -> Dict[str, Any]:
    """Parse le fichier de review pour extraire les données"""
    content = filepath.read_text(encoding='utf-8')
    
    # Extraire les sections
    data = {
        "fr": {},
        "en": {}
    }
    
    # Version FR - Extraire depuis "## Champs Sanity" jusqu'au "---" avant "## Version ANGLAISE"
    fr_section = re.search(r'## Champs Sanity \(Version FRANÇAISE\)(.*?)(?=\n---\n\n## Version ANGLAISE)', content, re.DOTALL)
    if fr_section:
        fr_text = fr_section.group(1)
        
        # Title
        title_match = re.search(r'### Title\n(.+?)(?=\n###)', fr_text, re.DOTALL)
        if title_match:
            data["fr"]["title"] = title_match.group(1).strip()
        
        # Slug
        slug_match = re.search(r'### Slug\n(.+?)(?=\n###)', fr_text, re.DOTALL)
        if slug_match:
            data["fr"]["slug"] = slug_match.group(1).strip()
        
        # Excerpt
        excerpt_match = re.search(r'### Excerpt\n(.+?)(?=\n###)', fr_text, re.DOTALL)
        if excerpt_match:
            data["fr"]["excerpt"] = excerpt_match.group(1).strip()
        
        # Meta Title
        meta_title_match = re.search(r'### Meta Title.*?\n(.+?)(?=\*Longueur)', fr_text, re.DOTALL)
        if meta_title_match:
            data["fr"]["metaTitle"] = meta_title_match.group(1).strip()
        
        # Meta Description
        meta_desc_match = re.search(r'### Meta Description.*?\n(.+?)(?=\*Longueur)', fr_text, re.DOTALL)
        if meta_desc_match:
            data["fr"]["metaDescription"] = meta_desc_match.group(1).strip()
        
        # Canonical URL
        canonical_match = re.search(r'### Canonical URL\n(.+?)(?=\n###)', fr_text, re.DOTALL)
        if canonical_match:
            data["fr"]["canonicalUrl"] = canonical_match.group(1).strip()
        
        # OG Title
        og_title_match = re.search(r'#### OG Title\n(.+?)(?=\n####)', fr_text, re.DOTALL)
        if og_title_match:
            data["fr"]["ogTitle"] = og_title_match.group(1).strip()
        
        # OG Description
        og_desc_match = re.search(r'#### OG Description\n(.+?)(?=\n####)', fr_text, re.DOTALL)
        if og_desc_match:
            data["fr"]["ogDescription"] = og_desc_match.group(1).strip()
        
        # Translation Group
        tg_match = re.search(r'### Translation Group\n(.+?)(?=\n###)', fr_text, re.DOTALL)
        if tg_match:
            data["fr"]["translationGroup"] = tg_match.group(1).strip()
        
        # Published at
        published_at_match = re.search(r'### Published at\n(.+?)(?=\n###)', fr_text, re.DOTALL)
        if published_at_match:
            pub_date_str = published_at_match.group(1).strip()
            # Convertir "2025-12-11 14:06" en ISO format "2025-12-11T14:06:00"
            try:
                # Essayer différents formats
                for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]:
                    try:
                        dt = datetime.strptime(pub_date_str, fmt)
                        data["fr"]["publishedAt"] = dt.isoformat()
                        break
                    except ValueError:
                        continue
                else:
                    # Si aucun format ne fonctionne, utiliser la date actuelle
                    data["fr"]["publishedAt"] = datetime.now().isoformat()
            except:
                data["fr"]["publishedAt"] = datetime.now().isoformat()
        else:
            data["fr"]["publishedAt"] = datetime.now().isoformat()
        
        # Body - extraire tout le contenu après "### Body\n" jusqu'au séparateur "---"
        body_match = re.search(r'### Body\n(.*?)(?=\n---|\n## Version)', fr_text, re.DOTALL)
        if body_match:
            data["fr"]["body"] = body_match.group(1).strip()
        else:
            # Fallback: chercher juste après "### Body"
            body_match2 = re.search(r'### Body\n(.*)', fr_text, re.DOTALL)
            if body_match2:
                body_content = body_match2.group(1)
                # S'arrêter au "---" ou à la section suivante
                if '---' in body_content:
                    body_content = body_content.split('---')[0]
                elif '## Version' in body_content:
                    body_content = body_content.split('## Version')[0]
                data["fr"]["body"] = body_content.strip()
    
    # Version EN
    en_section = re.search(r'## Version ANGLAISE(.*?)(?=\n---|\n## Métadonnées)', content, re.DOTALL)
    if en_section:
        en_text = en_section.group(1)
        
        # Title
        title_match = re.search(r'### Title\n(.+?)(?=\n###)', en_text, re.DOTALL)
        if title_match:
            data["en"]["title"] = title_match.group(1).strip()
        
        # Slug
        slug_match = re.search(r'### Slug\n(.+?)(?=\n###)', en_text, re.DOTALL)
        if slug_match:
            data["en"]["slug"] = slug_match.group(1).strip()
        
        # Excerpt
        excerpt_match = re.search(r'### Excerpt\n(.+?)(?=\n###)', en_text, re.DOTALL)
        if excerpt_match:
            data["en"]["excerpt"] = excerpt_match.group(1).strip()
        
        # Meta Title
        meta_title_match = re.search(r'### Meta Title\n(.+?)(?=\n###)', en_text, re.DOTALL)
        if meta_title_match:
            data["en"]["metaTitle"] = meta_title_match.group(1).strip()
        
        # Meta Description
        meta_desc_match = re.search(r'### Meta Description\n(.+?)(?=\n###)', en_text, re.DOTALL)
        if meta_desc_match:
            data["en"]["metaDescription"] = meta_desc_match.group(1).strip()
        
        # Canonical URL
        canonical_match = re.search(r'### Canonical URL\n(.+?)(?=\n###)', en_text, re.DOTALL)
        if canonical_match:
            data["en"]["canonicalUrl"] = canonical_match.group(1).strip()
        
        # OG Title
        og_title_match = re.search(r'### OG Title\n(.+?)(?=\n###)', en_text, re.DOTALL)
        if og_title_match:
            data["en"]["ogTitle"] = og_title_match.group(1).strip()
        
        # OG Description
        og_desc_match = re.search(r'### OG Description\n(.+?)(?=\n###)', en_text, re.DOTALL)
        if og_desc_match:
            data["en"]["ogDescription"] = og_desc_match.group(1).strip()
        
        # Translation Group (doit être identique à FR)
        data["en"]["translationGroup"] = data["fr"].get("translationGroup", "")
        
        # Published at (même date que FR)
        data["en"]["publishedAt"] = data["fr"].get("publishedAt", datetime.now().isoformat())
        
        # Body
        body_match = re.search(r'### Body\n(.*?)(?=\n---|\Z)', en_text, re.DOTALL)
        if body_match:
            data["en"]["body"] = body_match.group(1).strip()
    
    return data


def fetch_sanity_references():
    """Récupère les références Sanity"""
    url = f"{SANITY_API_URL}/data/query/{SANITY_DATASET}"
    headers = {
        "Authorization": f"Bearer {SANITY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    groq_query = """{
      "category": *[_type == "category" && slug.current == "guides-pratiques"][0]._id,
      "author": *[_type == "author" && name == "Matthieu HUBERT"][0]._id
    }"""
    
    payload = {
        "query": groq_query,
        "params": {}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get("result", {})
    except Exception as e:
        print(f"⚠️  Erreur récupération références: {e}")
    
    return {"category": None, "author": None}


def publish_article(article_data: Dict[str, Any], language: str, references: Dict[str, Any]) -> bool:
    """Publie un article en production"""
    print(f"\n🚀 Publication version {language.upper()}...")
    
    slug = article_data.get("slug", "")
    
    # Pour les versions EN, utiliser le slug du canonical URL si disponible
    # (car il peut contenir le suffixe -en nécessaire pour l'URL)
    if language == "en":
        canonical_url = article_data.get("canonicalUrl", "")
        if canonical_url:
            import urllib.parse
            path = urllib.parse.urlparse(canonical_url).path
            # Extraire le slug depuis le chemin (ex: /blog/slug-en -> slug-en)
            path_parts = [p for p in path.strip("/").split("/") if p]
            if path_parts:
                slug_from_url = path_parts[-1]
                # Toujours utiliser le slug du canonical URL pour EN (il peut contenir -en)
                if slug_from_url and slug_from_url.endswith("-en"):
                    print(f"📝 Utilisation du slug du canonical URL: {slug_from_url}")
                    slug = slug_from_url
    
    base_id = slug.replace("-", "_") if slug else str(uuid.uuid4())[:8]
    document_id = base_id
    
    # Convertir le body en format Block Content
    body_text = article_data.get("body", "")
    # Ajouter lien Markdown si le texte "Découvrir Donna" est présent
    if "Découvrir Donna" in body_text and "callrounded.com/cas-usage/secretariat-medical" not in body_text:
        body_text = body_text.replace(
            "Découvrir Donna",
            "[Découvrir Donna](https://callrounded.com/cas-usage/secretariat-medical)"
        )
    try:
        body_blocks = convert_text_to_sanity_blocks(body_text)
    except Exception as e:
        print(f"⚠️  Erreur conversion Block Content: {e}")
        # Fallback: bloc simple
        body_blocks = [{
            "_key": generate_key(),
            "_type": "block",
            "style": "normal",
            "children": [{"_key": generate_key(), "_type": "span", "text": body_text[:500], "marks": []}],
            "markDefs": []
        }]
    
    post_data = {
        "_id": document_id,
        "_type": "post",
        "title": article_data.get("title", ""),
        "slug": {
            "_type": "slug",
            "current": slug
        },
        "excerpt": article_data.get("excerpt", ""),
        "body": body_blocks,  # Format Block Content
        "publishedAt": article_data.get("publishedAt", datetime.now().isoformat()),
        
        # Métadonnées SEO
        "metaTitle": article_data.get("metaTitle", "")[:60],
        "metaDescription": article_data.get("metaDescription", "")[:160],
        
        # Canonical URL
        "canonicalUrl": article_data.get("canonicalUrl", f"https://callrounded.com/blog/{slug}"),
        
        # Translation Group
        "translationGroup": article_data.get("translationGroup", slug),
        
        # Language
        "language": language
    }
    
    # Open Graph - seulement si le schéma les accepte (commenté pour éviter l'erreur)
    # "ogTitle": article_data.get("ogTitle", ""),
    # "ogDescription": article_data.get("ogDescription", "")[:160],
    # "ogType": "article",
    
    # Robots - seulement si le schéma l'accepte (commenté pour éviter l'erreur)
    # "robots": {
    #     "noindex": False,
    #     "nofollow": False
    # }
    
    # Ajouter références
    if references.get("author"):
        post_data["author"] = {
            "_type": "reference",
            "_ref": references["author"]
        }
    if references.get("category"):
        post_data["categories"] = [{
            "_key": generate_key(),
            "_type": "reference",
            "_ref": references["category"]
        }]
    
    # Utiliser createOrReplace pour mettre à jour si existe déjà
    mutation = {
        "mutations": [{
            "createOrReplace": post_data
        }]
    }
    
    url = f"{SANITY_API_URL}/data/mutate/{SANITY_DATASET}"
    headers = {
        "Authorization": f"Bearer {SANITY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=mutation, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Article {language.upper()} publié !")
            print(f"   ID: {document_id}")
            print(f"   Titre: {article_data.get('title', 'N/A')}")
            print(f"   Slug: {slug}")
            print(f"   Transaction: {result.get('transactionId', 'N/A')}")
            
            # Révalider le site Next.js pour que l'article apparaisse immédiatement
            revalidate_nextjs(slug)
            
            return True
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def revalidate_nextjs(slug: str):
    """Révalide le site Next.js pour que l'article apparaisse"""
    # URL de revalidation Next.js (si configurée)
    revalidate_url = os.getenv("REVALIDATE_URL")
    
    if not revalidate_url:
        print("⚠️  REVALIDATE_URL non configurée - l'article pourrait prendre quelques minutes à apparaître")
        return
    
    try:
        print(f"\n🔄 Révalidation Next.js pour: {slug}")
        response = requests.post(
            revalidate_url,
            json={"slug": slug},
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Site révalidé avec succès")
        else:
            print(f"⚠️  Révalidation échouée ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"⚠️  Erreur révalidation (non bloquante): {e}")


def main():
    """Publie l'article depuis le fichier"""
    # Par défaut, utiliser le dernier article généré
    articles_dir = Path(__file__).parent.parent / "articles"
    articles = sorted(articles_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if len(sys.argv) > 1:
        filepath = Path(sys.argv[1])
    else:
        if not articles:
            print("❌ Aucun article trouvé dans le dossier articles/")
            print("Usage: python3 scripts/publish_from_file.py <chemin_vers_fichier_md>")
            sys.exit(1)
        filepath = articles[0]
    
    if not filepath.exists():
        print(f"❌ Fichier non trouvé: {filepath}")
        sys.exit(1)
    
    print("=" * 70)
    print("🚀 PUBLICATION DIRECTE DEPUIS LE FICHIER DE REVIEW")
    print("=" * 70)
    print()
    
    # Parser le fichier
    print("📖 Lecture du fichier...")
    data = parse_review_file(filepath)
    
    if not data["fr"]:
        print("❌ Impossible de parser la version FR")
        sys.exit(1)
    
    print(f"✅ Version FR trouvée: {data['fr'].get('title', 'N/A')}")
    if data["en"]:
        print(f"✅ Version EN trouvée: {data['en'].get('title', 'N/A')}")
    
    # Récupérer les références
    print("\n🔗 Récupération des références Sanity...")
    references = fetch_sanity_references()
    print("✅ Références récupérées\n")
    
    # Publier FR
    success_fr = publish_article(data["fr"], "fr", references)
    
    if success_fr and data["en"]:
        # Publier EN
        success_en = publish_article(data["en"], "en", references)
        
        if success_en:
            print()
            print("=" * 70)
            print("✅ TERMINÉ - Articles publiés (FR + EN) !")
            print("=" * 70)
            print(f"\n🔗 Translation Group: {data['fr'].get('translationGroup', 'N/A')}")
            
            # Ajouter à la base de connaissances
            add_to_knowledge_base(data["fr"]["title"], data["fr"]["slug"])
        else:
            print()
            print("=" * 70)
            print("⚠️  Version FR publiée, mais erreur sur version EN")
            print("=" * 70)
    elif success_fr:
        print()
        print("=" * 70)
        print("✅ TERMINÉ - Article FR publié !")
        print("=" * 70)
        
        # Ajouter à la base de connaissances
        add_to_knowledge_base(data["fr"]["title"], data["fr"]["slug"])
    else:
        print()
        print("=" * 70)
        print("❌ ERREUR lors de la publication FR")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()

