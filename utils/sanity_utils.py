"""
Utilitaires pour convertir le contenu HTML en format Sanity Block Content
"""

import re
from typing import List, Dict, Any
import random
import string


def generate_key():
    """Génère une clé unique"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def html_to_sanity_blocks(html_content: str) -> List[Dict[str, Any]]:
    """
    Convertit du HTML en format Sanity Block Content structuré
    """
    blocks = []
    
    # Séparer le contenu par balises HTML
    # Pattern pour extraire les éléments HTML
    pattern = r'<(h2|h3|p|ul|li|strong)([^>]*)>(.*?)</\1>'
    
    lines = html_content.split('\n')
    current_block = None
    current_list_items = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # H2
        h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', line, re.IGNORECASE)
        if h2_match:
            if current_block:
                blocks.append(current_block)
            blocks.append({
                "_key": generate_key(),
                "_type": "block",
                "style": "h2",
                "children": [{
                    "_key": generate_key(),
                    "_type": "span",
                    "text": clean_html(h2_match.group(1)),
                    "marks": []
                }],
                "markDefs": []
            })
            current_block = None
            continue
        
        # H3
        h3_match = re.search(r'<h3[^>]*>(.*?)</h3>', line, re.IGNORECASE)
        if h3_match:
            if current_block:
                blocks.append(current_block)
            blocks.append({
                "_key": generate_key(),
                "_type": "block",
                "style": "h3",
                "children": [{
                    "_key": generate_key(),
                    "_type": "span",
                    "text": clean_html(h3_match.group(1)),
                    "marks": []
                }],
                "markDefs": []
            })
            current_block = None
            continue
        
        # Liste UL
        ul_match = re.search(r'<ul[^>]*>(.*?)</ul>', line, re.DOTALL | re.IGNORECASE)
        if ul_match:
            # Extraire les items de la liste
            li_pattern = r'<li[^>]*>(.*?)</li>'
            items = re.findall(li_pattern, ul_match.group(1), re.DOTALL | re.IGNORECASE)
            
            for item in items:
                # Parser le texte avec les marks (strong, liens)
                parsed = parse_text_with_marks(item)
                children = parsed["children"] if isinstance(parsed, dict) else parsed
                mark_defs = parsed.get("mark_defs", []) if isinstance(parsed, dict) else []
                
                blocks.append({
                    "_key": generate_key(),
                    "_type": "block",
                    "style": "normal",
                    "listItem": "bullet",
                    "children": children,
                    "markDefs": mark_defs
                })
            current_block = None
            continue
        
        # Paragraphe
        p_match = re.search(r'<p[^>]*>(.*?)</p>', line, re.DOTALL | re.IGNORECASE)
        if p_match:
            if current_block:
                blocks.append(current_block)
            
            para_text = p_match.group(1)
            # Extraire les balises strong (gras) et les liens
            parsed = parse_text_with_marks(para_text)
            children = parsed["children"] if isinstance(parsed, dict) else parsed
            mark_defs = parsed.get("mark_defs", []) if isinstance(parsed, dict) else []
            
            blocks.append({
                "_key": generate_key(),
                "_type": "block",
                "style": "normal",
                "children": children,
                "markDefs": mark_defs
            })
            current_block = None
            continue
        
        # Texte brut (si pas de balises)
        if not re.search(r'<[^>]+>', line):
            text = line.strip()
            if text:
                if current_block:
                    blocks.append(current_block)
                blocks.append({
                    "_key": generate_key(),
                    "_type": "block",
                    "style": "normal",
                    "children": [{
                        "_key": generate_key(),
                        "_type": "span",
                        "text": text,
                        "marks": []
                    }],
                    "markDefs": []
                })
                current_block = None
    
    if current_block:
        blocks.append(current_block)
    
    # Si aucun bloc créé, créer un bloc simple avec tout le texte
    if not blocks:
        blocks.append({
            "_key": generate_key(),
            "_type": "block",
            "style": "normal",
            "children": [{
                "_key": generate_key(),
                "_type": "span",
                "text": clean_html(html_content),
                "marks": []
            }],
            "markDefs": []
        })
    
    return blocks


def parse_text_with_marks(text: str) -> Dict[str, Any]:
    """
    Parse le texte et extrait les balises strong et les liens pour créer des marks
    Retourne un dict avec 'children' et 'mark_defs'
    """
    from typing import Dict, Any
    
    children = []
    mark_defs = []
    mark_index = 0
    
    # Fonction récursive pour parser le texte
    def parse_recursive(content: str, in_strong: bool = False):
        nonlocal mark_index
        
        # Chercher les balises dans l'ordre d'apparition
        parts = []
        pos = 0
        
        # Pattern pour trouver strong ou link
        pattern = r'(<strong[^>]*>.*?</strong>|<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>)'
        matches = list(re.finditer(pattern, content, re.IGNORECASE | re.DOTALL))
        
        if not matches:
            # Pas de balises, juste du texte
            clean = clean_html(content)
            if clean:
                return [{
                    "_key": generate_key(),
                    "_type": "span",
                    "text": clean,
                    "marks": ["strong"] if in_strong else []
                }]
            return []
        
        result = []
        last_pos = 0
        
        for match in matches:
            # Texte avant la balise
            if match.start() > last_pos:
                before_text = content[last_pos:match.start()]
                clean_before = clean_html(before_text)
                if clean_before:
                    result.append({
                        "_key": generate_key(),
                        "_type": "span",
                        "text": clean_before,
                        "marks": ["strong"] if in_strong else []
                    })
            
            matched = match.group(0)
            
            # Si c'est un strong
            if matched.startswith('<strong'):
                strong_content = re.search(r'<strong[^>]*>(.*?)</strong>', matched, re.IGNORECASE | re.DOTALL)
                if strong_content:
                    inner = strong_content.group(1)
                    # Vérifier si le strong contient un lien
                    link_in = re.search(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', inner, re.IGNORECASE | re.DOTALL)
                    if link_in:
                        # Lien dans un strong
                        link_url = link_in.group(1)
                        link_text = clean_html(link_in.group(2))
                        mark_key = f"link_{mark_index}"
                        mark_index += 1
                        mark_defs.append({
                            "_key": mark_key,
                            "_type": "link",
                            "href": link_url
                        })
                        result.append({
                            "_key": generate_key(),
                            "_type": "span",
                            "text": link_text,
                            "marks": ["strong", mark_key]
                        })
                    else:
                        # Juste du strong, parser récursivement
                        parsed = parse_recursive(inner, in_strong=True)
                        result.extend(parsed)
            
            # Si c'est un lien
            elif matched.startswith('<a'):
                link_match = re.search(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', matched, re.IGNORECASE | re.DOTALL)
                if link_match:
                    link_url = link_match.group(1)
                    link_text = clean_html(link_match.group(2))
                    mark_key = f"link_{mark_index}"
                    mark_index += 1
                    mark_defs.append({
                        "_key": mark_key,
                        "_type": "link",
                        "href": link_url
                    })
                    result.append({
                        "_key": generate_key(),
                        "_type": "span",
                        "text": link_text,
                        "marks": (["strong"] if in_strong else []) + [mark_key]
                    })
            
            last_pos = match.end()
        
        # Texte après la dernière balise
        if last_pos < len(content):
            after_text = content[last_pos:]
            clean_after = clean_html(after_text)
            if clean_after:
                result.append({
                    "_key": generate_key(),
                    "_type": "span",
                    "text": clean_after,
                    "marks": ["strong"] if in_strong else []
                })
        
        return result
    
    children = parse_recursive(text)
    
    # Si aucun enfant, créer un span par défaut
    if not children:
        children = [{
            "_key": generate_key(),
            "_type": "span",
            "text": clean_html(text),
            "marks": []
        }]
    
    return {
        "children": children,
        "mark_defs": mark_defs
    }


def clean_html(text: str) -> str:
    """Nettoie le HTML et retourne le texte brut"""
    # Enlever toutes les balises HTML
    text = re.sub(r'<[^>]+>', '', text)
    # Décoder les entités HTML
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    # Nettoyer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def create_mark_defs() -> List[Dict[str, Any]]:
    """Crée les définitions de marks pour Sanity"""
    return [
        {
            "_key": "strong",
            "_type": "strong"
        }
    ]

