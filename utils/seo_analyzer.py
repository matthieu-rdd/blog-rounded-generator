#!/usr/bin/env python3
"""
Analyse SEO avancée pour les articles
- Densité des mots-clés
- Suggestions LSI
- Score de lisibilité (Flesch Reading Ease)
- Vérification longueur optimale
- Détection liens internes
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import math


def calculate_keyword_density(text: str, keywords: List[str]) -> Dict[str, float]:
    """
    Calcule la densité de chaque mot-clé dans le texte
    
    Returns:
        {
            "keyword": density_percentage,
            ...
        }
    """
    text_lower = text.lower()
    total_words = len(text.split())
    
    densities = {}
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Compter les occurrences (mots complets uniquement)
        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
        count = len(re.findall(pattern, text_lower))
        density = (count / total_words * 100) if total_words > 0 else 0
        densities[keyword] = round(density, 2)
    
    return densities


def suggest_lsi_keywords(text: str, main_keyword: str, max_suggestions: int = 5) -> List[str]:
    """
    Suggère des mots-clés LSI (Latent Semantic Indexing) basés sur le contenu
    
    Analyse les mots fréquents qui apparaissent souvent avec le mot-clé principal
    """
    text_lower = text.lower()
    main_keyword_lower = main_keyword.lower()
    
    # Extraire les phrases contenant le mot-clé principal
    sentences = re.split(r'[.!?]+\s+', text)
    relevant_sentences = [s for s in sentences if main_keyword_lower in s.lower()]
    
    if not relevant_sentences:
        return []
    
    # Extraire les mots (2-3 mots) qui apparaissent souvent avec le mot-clé
    words_pattern = re.compile(r'\b[a-zàâäéèêëïîôùûüÿç]{4,}\b', re.IGNORECASE)
    
    co_occurring_words = []
    for sentence in relevant_sentences:
        words = words_pattern.findall(sentence.lower())
        # Filtrer les mots communs et le mot-clé principal
        stop_words = {'pour', 'avec', 'dans', 'sur', 'par', 'une', 'les', 'des', 'est', 'sont', 
                     'cette', 'ces', 'leur', 'leurs', 'plus', 'tout', 'tous', 'toutes', 'être',
                     'avoir', 'faire', 'peut', 'peuvent', 'doit', 'doivent', 'comme', 'quand'}
        filtered_words = [w for w in words if w not in stop_words and w != main_keyword_lower]
        co_occurring_words.extend(filtered_words)
    
    # Compter les occurrences et prendre les plus fréquents
    word_counts = Counter(co_occurring_words)
    top_words = [word for word, count in word_counts.most_common(max_suggestions * 2)]
    
    # Créer des bigrammes et trigrammes avec le mot-clé principal
    suggestions = []
    for word in top_words[:max_suggestions]:
        # Créer des combinaisons
        if len(word) > 4:  # Éviter les mots trop courts
            suggestions.append(f"{main_keyword} {word}")
            suggestions.append(word)
    
    return list(set(suggestions))[:max_suggestions]


def calculate_flesch_reading_ease(text: str) -> Dict[str, Any]:
    """
    Calcule le score de lisibilité Flesch Reading Ease
    
    Score:
    - 90-100 : Très facile (5ème année)
    - 80-89 : Facile (6ème année)
    - 70-79 : Assez facile (7ème année)
    - 60-69 : Standard (8ème-9ème année)
    - 50-59 : Assez difficile (Lycée)
    - 30-49 : Difficile (Université)
    - 0-29 : Très difficile (Université avancée)
    
    Returns:
        {
            "score": float,
            "level": str,
            "sentences": int,
            "words": int,
            "syllables": int,
            "avg_sentence_length": float,
            "avg_syllables_per_word": float
        }
    """
    # Compter les phrases
    sentences = re.split(r'[.!?]+\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = len(sentences)
    
    # Compter les mots
    words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿç]+\b', text.lower())
    num_words = len(words)
    
    if num_sentences == 0 or num_words == 0:
        return {
            "score": 0,
            "level": "Non calculable",
            "sentences": 0,
            "words": 0,
            "syllables": 0,
            "avg_sentence_length": 0,
            "avg_syllables_per_word": 0
        }
    
    # Compter les syllabes (approximation pour le français)
    def count_syllables_fr(word: str) -> int:
        """Estime le nombre de syllabes en français"""
        word = word.lower()
        # Règles simplifiées pour le français
        vowels = 'aeiouyàâäéèêëïîôùûüÿ'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Minimum 1 syllabe
        return max(1, syllable_count)
    
    total_syllables = sum(count_syllables_fr(word) for word in words)
    
    # Calculer le score Flesch (adapté pour le français)
    # Formule simplifiée : 206.835 - (1.015 * ASL) - (84.6 * ASW)
    # ASL = Average Sentence Length (mots par phrase)
    # ASW = Average Syllables per Word
    
    avg_sentence_length = num_words / num_sentences
    avg_syllables_per_word = total_syllables / num_words
    
    # Score adapté (formule simplifiée)
    score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    score = max(0, min(100, score))
    
    # Déterminer le niveau
    if score >= 90:
        level = "Très facile"
    elif score >= 80:
        level = "Facile"
    elif score >= 70:
        level = "Assez facile"
    elif score >= 60:
        level = "Standard"
    elif score >= 50:
        level = "Assez difficile"
    elif score >= 30:
        level = "Difficile"
    else:
        level = "Très difficile"
    
    return {
        "score": round(score, 1),
        "level": level,
        "sentences": num_sentences,
        "words": num_words,
        "syllables": total_syllables,
        "avg_sentence_length": round(avg_sentence_length, 1),
        "avg_syllables_per_word": round(avg_syllables_per_word, 2)
    }


def check_optimal_lengths(title: str, meta_title: str, meta_description: str) -> Dict[str, Any]:
    """
    Vérifie si les longueurs sont optimales pour le SEO
    
    Returns:
        {
            "title": {"length": int, "optimal": bool, "recommendation": str},
            "meta_title": {"length": int, "optimal": bool, "recommendation": str},
            "meta_description": {"length": int, "optimal": bool, "recommendation": str}
        }
    """
    def check_length(text: str, min_len: int, max_len: int, field_name: str) -> Dict[str, Any]:
        length = len(text)
        optimal = min_len <= length <= max_len
        
        if length < min_len:
            recommendation = f"Trop court ({length} chars). Ajoutez {min_len - length} caractères minimum."
        elif length > max_len:
            recommendation = f"Trop long ({length} chars). Réduisez de {length - max_len} caractères."
        else:
            recommendation = f"Longueur optimale ({length} chars)"
        
        return {
            "length": length,
            "optimal": optimal,
            "recommendation": recommendation,
            "min": min_len,
            "max": max_len
        }
    
    return {
        "title": check_length(title, 30, 65, "Titre"),
        "meta_title": check_length(meta_title, 50, 60, "Meta Title"),
        "meta_description": check_length(meta_description, 155, 160, "Meta Description")
    }


def detect_internal_links(text: str, base_domain: str = "callrounded.com") -> Dict[str, Any]:
    """
    Détecte les liens internes dans le texte
    
    Returns:
        {
            "internal_links": List[str],
            "external_links": List[str],
            "total_links": int,
            "internal_count": int,
            "external_count": int,
            "recommendation": str
        }
    """
    # Pattern pour détecter les liens markdown [texte](url)
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    links = re.findall(link_pattern, text)
    
    internal_links = []
    external_links = []
    
    for text_link, url in links:
        if base_domain in url.lower():
            internal_links.append({"text": text_link, "url": url})
        else:
            external_links.append({"text": text_link, "url": url})
    
    total_links = len(links)
    internal_count = len(internal_links)
    external_count = len(external_links)
    
    # Recommandation
    if internal_count == 0 and total_links > 0:
        recommendation = "Aucun lien interne détecté. Ajoutez des liens vers d'autres articles du blog."
    elif internal_count < 2:
        recommendation = f"Seulement {internal_count} lien(s) interne(s). Ajoutez 2-3 liens internes pour améliorer le SEO."
    else:
        recommendation = f"✅ {internal_count} lien(s) interne(s) détecté(s). Bon pour le SEO."
    
    return {
        "internal_links": internal_links,
        "external_links": external_links,
        "total_links": total_links,
        "internal_count": internal_count,
        "external_count": external_count,
        "recommendation": recommendation
    }


def analyze_seo_comprehensive(
    article_text: str,
    title: str,
    meta_title: str,
    meta_description: str,
    target_keywords: List[str],
    main_keyword: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyse SEO complète de l'article
    
    Returns:
        {
            "keyword_density": {...},
            "lsi_suggestions": [...],
            "readability": {...},
            "lengths": {...},
            "links": {...},
            "overall_score": float,
            "recommendations": List[str]
        }
    """
    # Densité des mots-clés
    keyword_density = calculate_keyword_density(article_text, target_keywords)
    
    # Suggestions LSI
    main_kw = main_keyword or (target_keywords[0] if target_keywords else "")
    lsi_suggestions = suggest_lsi_keywords(article_text, main_kw) if main_kw else []
    
    # Lisibilité
    readability = calculate_flesch_reading_ease(article_text)
    
    # Longueurs optimales
    lengths = check_optimal_lengths(title, meta_title, meta_description)
    
    # Liens internes
    links = detect_internal_links(article_text)
    
    # Score global (0-100)
    score_components = []
    
    # Densité des mots-clés (0-30 points)
    if keyword_density:
        main_density = keyword_density.get(main_kw, 0) if main_kw else 0
        if 1.0 <= main_density <= 2.0:
            score_components.append(30)
        elif 0.5 <= main_density < 1.0 or 2.0 < main_density <= 3.0:
            score_components.append(20)
        else:
            score_components.append(10)
    else:
        score_components.append(0)
    
    # Lisibilité (0-20 points)
    if readability["score"] >= 60:
        score_components.append(20)
    elif readability["score"] >= 50:
        score_components.append(15)
    elif readability["score"] >= 40:
        score_components.append(10)
    else:
        score_components.append(5)
    
    # Longueurs (0-20 points)
    lengths_score = 0
    if lengths["title"]["optimal"]:
        lengths_score += 7
    if lengths["meta_title"]["optimal"]:
        lengths_score += 7
    if lengths["meta_description"]["optimal"]:
        lengths_score += 6
    score_components.append(lengths_score)
    
    # Liens internes (0-15 points)
    if links["internal_count"] >= 3:
        score_components.append(15)
    elif links["internal_count"] >= 2:
        score_components.append(10)
    elif links["internal_count"] >= 1:
        score_components.append(5)
    else:
        score_components.append(0)
    
    # Structure (H2/H3) (0-15 points)
    h2_count = len(re.findall(r'^##\s+', article_text, re.MULTILINE))
    h3_count = len(re.findall(r'^###\s+', article_text, re.MULTILINE))
    if h2_count >= 3 and h3_count >= 2:
        score_components.append(15)
    elif h2_count >= 2:
        score_components.append(10)
    elif h2_count >= 1:
        score_components.append(5)
    else:
        score_components.append(0)
    
    overall_score = sum(score_components)
    
    # Recommandations
    recommendations = []
    
    if keyword_density:
        main_density_val = keyword_density.get(main_kw, 0) if main_kw else 0
        if main_density_val < 1.0:
            recommendations.append(f"Augmentez la densité du mot-clé principal '{main_kw}' (actuellement {main_density_val}%, cible: 1-2%)")
        elif main_density_val > 2.5:
            recommendations.append(f"Réduisez la densité du mot-clé principal '{main_kw}' (actuellement {main_density_val}%, risque de sur-optimisation)")
    
    if readability["score"] < 50:
        recommendations.append(f"Améliorez la lisibilité (score: {readability['score']}, niveau: {readability['level']}). Utilisez des phrases plus courtes.")
    
    if not lengths["title"]["optimal"]:
        recommendations.append(f"Titre: {lengths['title']['recommendation']}")
    if not lengths["meta_title"]["optimal"]:
        recommendations.append(f"Meta Title: {lengths['meta_title']['recommendation']}")
    if not lengths["meta_description"]["optimal"]:
        recommendations.append(f"Meta Description: {lengths['meta_description']['recommendation']}")
    
    if links["internal_count"] < 2:
        recommendations.append(links["recommendation"])
    
    if h2_count < 2:
        recommendations.append(f"Ajoutez au moins 2-3 titres H2 pour améliorer la structure")
    
    return {
        "keyword_density": keyword_density,
        "lsi_suggestions": lsi_suggestions,
        "readability": readability,
        "lengths": lengths,
        "links": links,
        "structure": {
            "h2_count": h2_count,
            "h3_count": h3_count
        },
        "overall_score": overall_score,
        "recommendations": recommendations
    }
