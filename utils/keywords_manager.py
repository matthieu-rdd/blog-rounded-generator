#!/usr/bin/env python3
"""
Gestionnaire de mots-clés avec métadonnées SEO
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
KEYWORDS_METADATA_FILE = BASE_DIR / "data" / "keywords_metadata.json"
KEYWORDS_FILE = BASE_DIR / "data" / "keywords.json"
ARTICLES_DIR = BASE_DIR / "articles"


def load_keywords_metadata() -> Dict[str, Dict[str, Any]]:
    """Charge les métadonnées des mots-clés"""
    if not KEYWORDS_METADATA_FILE.exists():
        return {}
    
    try:
        with open(KEYWORDS_METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Erreur chargement métadonnées mots-clés: {e}")
        return {}


def save_keywords_metadata(metadata: Dict[str, Dict[str, Any]]):
    """Sauvegarde les métadonnées des mots-clés"""
    try:
        KEYWORDS_METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(KEYWORDS_METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️  Erreur sauvegarde métadonnées mots-clés: {e}")


def load_keywords_list() -> List[str]:
    """Charge la liste des mots-clés depuis keywords.json"""
    if not KEYWORDS_FILE.exists():
        return []
    
    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get("default", [])
        return []
    except Exception as e:
        print(f"⚠️  Erreur chargement mots-clés: {e}")
        return []


def save_keywords_list(keywords: List[str]):
    """Sauvegarde la liste des mots-clés dans keywords.json"""
    try:
        KEYWORDS_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {"default": keywords}
        with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️  Erreur sauvegarde mots-clés: {e}")


def count_keyword_in_articles(keyword: str) -> Dict[str, Any]:
    """
    Compte les occurrences d'un mot-clé dans les articles existants
    
    Returns:
        {
            "total_occurrences": int,
            "articles_count": int,
            "articles": List[str]  # noms des fichiers
        }
    """
    if not ARTICLES_DIR.exists():
        return {"total_occurrences": 0, "articles_count": 0, "articles": []}
    
    keyword_lower = keyword.lower()
    total_occurrences = 0
    articles_with_keyword = []
    
    for article_file in ARTICLES_DIR.glob("*.md"):
        try:
            content = article_file.read_text(encoding="utf-8").lower()
            # Compter les occurrences (insensible à la casse)
            count = len(re.findall(re.escape(keyword_lower), content))
            if count > 0:
                total_occurrences += count
                articles_with_keyword.append(article_file.name)
        except Exception as e:
            print(f"⚠️  Erreur lecture {article_file.name}: {e}")
    
    return {
        "total_occurrences": total_occurrences,
        "articles_count": len(articles_with_keyword),
        "articles": articles_with_keyword
    }


def calculate_blogs_needed(volume: Optional[int], complexity: Optional[str]) -> Optional[int]:
    """
    Calcule le nombre de blogs à créer basé sur le volume de recherche
    
    Logique simple :
    - Volume < 100 : 1-2 blogs
    - Volume 100-1000 : 2-5 blogs
    - Volume 1000-10000 : 5-10 blogs
    - Volume > 10000 : 10+ blogs
    
    La complexité SEO peut ajuster :
    - Facile : -20%
    - Moyen : base
    - Difficile : +30%
    """
    if volume is None:
        return None
    
    # Base calculation
    if volume < 100:
        base = 1
    elif volume < 1000:
        base = 3
    elif volume < 10000:
        base = 7
    else:
        base = 12
    
    # Adjust by complexity
    if complexity == "Facile":
        base = max(1, int(base * 0.8))
    elif complexity == "Difficile":
        base = int(base * 1.3)
    
    return base


def get_all_keywords_with_stats() -> List[Dict[str, Any]]:
    """
    Retourne tous les mots-clés avec leurs métadonnées et statistiques
    """
    keywords_list = load_keywords_list()
    metadata = load_keywords_metadata()
    
    result = []
    for keyword in keywords_list:
        keyword_meta = metadata.get(keyword, {})
        stats = count_keyword_in_articles(keyword)
        
        volume = keyword_meta.get("volume")
        complexity = keyword_meta.get("complexity")
        blogs_needed = calculate_blogs_needed(volume, complexity)
        
        result.append({
            "keyword": keyword,
            "volume": volume,
            "complexity": complexity,
            "blogs_needed": blogs_needed,
            "total_occurrences": stats["total_occurrences"],
            "articles_count": stats["articles_count"],
            "articles": stats["articles"]
        })
    
    return result


def add_keyword(keyword: str, volume: Optional[int] = None, complexity: Optional[str] = None):
    """Ajoute un nouveau mot-clé"""
    keywords_list = load_keywords_list()
    if keyword not in keywords_list:
        keywords_list.append(keyword)
        save_keywords_list(keywords_list)
    
    # Ajouter/update métadonnées
    metadata = load_keywords_metadata()
    if keyword not in metadata:
        metadata[keyword] = {}
    if volume is not None:
        metadata[keyword]["volume"] = volume
    if complexity:
        metadata[keyword]["complexity"] = complexity
    metadata[keyword]["created_at"] = datetime.now().isoformat()
    save_keywords_metadata(metadata)


def update_keyword(keyword: str, volume: Optional[int] = None, complexity: Optional[str] = None):
    """Met à jour les métadonnées d'un mot-clé"""
    metadata = load_keywords_metadata()
    if keyword not in metadata:
        metadata[keyword] = {}
    if volume is not None:
        metadata[keyword]["volume"] = volume
    if complexity:
        metadata[keyword]["complexity"] = complexity
    metadata[keyword]["updated_at"] = datetime.now().isoformat()
    save_keywords_metadata(metadata)


def delete_keyword(keyword: str):
    """Supprime un mot-clé"""
    keywords_list = load_keywords_list()
    if keyword in keywords_list:
        keywords_list.remove(keyword)
        save_keywords_list(keywords_list)
    
    # Supprimer métadonnées
    metadata = load_keywords_metadata()
    if keyword in metadata:
        del metadata[keyword]
        save_keywords_metadata(metadata)

