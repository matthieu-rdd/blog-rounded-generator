#!/usr/bin/env python3
"""
Interface Streamlit pour le générateur d'articles de blog Rounded
"""

import streamlit as st
import sys
import os
import re
from pathlib import Path
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Générateur de Blog Rounded",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ajouter le chemin du projet pour les imports
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))

# Import des fonctions du script generate_article.py
# On initialise les fonctions à None pour éviter les erreurs
generate_topic_variants = None
generate_article = None
optimize_seo = None
generate_english_version = None
search_web = None
search_web_with_sources = None
load_existing_articles = None
check_topic_exists = None
get_existing_blog_topics = None
publish_to_production = None
fetch_sanity_references = None
save_article_for_review = None
load_target_keywords = None
select_target_keywords = None
apply_style_refinement = None
score_article_quality = None
regenerate_article_with_scoring = None

try:
    # On importe le module directement
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "generate_article", 
        BASE_DIR / "scripts" / "generate_article.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError("Impossible de charger le module generate_article")
    
    generate_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generate_module)
    
    # Import des fonctions nécessaires
    generate_topic_variants = generate_module.generate_topic_variants
    generate_article = generate_module.generate_article
    optimize_seo = generate_module.optimize_seo
    generate_english_version = generate_module.generate_english_version
    search_web = generate_module.search_web
    search_web_with_sources = generate_module.search_web_with_sources
    load_existing_articles = generate_module.load_existing_articles
    check_topic_exists = generate_module.check_topic_exists
    get_existing_blog_topics = generate_module.get_existing_blog_topics
    publish_to_production = generate_module.publish_to_production
    fetch_sanity_references = generate_module.fetch_sanity_references
    save_article_for_review = generate_module.save_article_for_review
    load_target_keywords = generate_module.load_target_keywords
    select_target_keywords = generate_module.select_target_keywords
    apply_style_refinement = generate_module.apply_style_refinement
    score_article_quality = generate_module.score_article_quality
    regenerate_article_with_scoring = generate_module.regenerate_article_with_scoring
    
except Exception as e:
    # On stocke l'erreur pour l'afficher après l'authentification
    st.session_state.import_error = str(e)

# CSS personnalisé
st.markdown("""
<style>
    /* Réduire les espaces en haut de la page principale */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Réduire l'espace de la sidebar */
    [data-testid="stSidebar"] {
        padding-top: 0.5rem;
    }
    
    /* Réduire l'espace du header */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    /* Réduire l'espace du footer */
    footer {
        display: none;
    }
    
    /* Réduire les marges des éléments dans la sidebar */
    [data-testid="stSidebar"] > div {
        padding-top: 0.5rem;
    }
    
    /* Réduire l'espace entre les sections */
    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
        margin-top: 0;
    }
    .variant-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .variant-card:hover {
        border-color: #1f77b4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de l'état de session
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'step' not in st.session_state:
    st.session_state.step = 'input'
if 'variants' not in st.session_state:
    st.session_state.variants = []
if 'chosen_variant' not in st.session_state:
    st.session_state.chosen_variant = None
if 'final_article' not in st.session_state:
    st.session_state.final_article = None
if 'english_article' not in st.session_state:
    st.session_state.english_article = None
if 'web_results' not in st.session_state:
    st.session_state.web_results = ""
if 'web_sources' not in st.session_state:
    st.session_state.web_sources = []
if 'topic' not in st.session_state:
    st.session_state.topic = ""
if 'target_keywords' not in st.session_state:
    st.session_state.target_keywords = []
if 'page' not in st.session_state:
    st.session_state.page = 'create'
if 'selected_article' not in st.session_state:
    st.session_state.selected_article = None
if 'article_saved' not in st.session_state:
    st.session_state.article_saved = False
if 'saved_filepath' not in st.session_state:
    st.session_state.saved_filepath = None
if 'delete_article' not in st.session_state:
    st.session_state.delete_article = None
if 'edited_content_fr' not in st.session_state:
    st.session_state.edited_content_fr = None
if 'edited_content_en' not in st.session_state:
    st.session_state.edited_content_en = None
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'article_scoring_before' not in st.session_state:
    st.session_state.article_scoring_before = None
if 'article_scoring_after' not in st.session_state:
    st.session_state.article_scoring_after = None

# Sidebar avec informations
with st.sidebar:
    st.markdown("### Rounded")
    st.markdown("---")
    st.markdown("#### Navigation")
    st.markdown("---")
    
    # Navigation entre pages
    page = st.radio(
        "Choisir une page",
        ["Créer un article", "Historique", "Analytics", "Tokens OpenAI", "Mots-clés SEO"],
        label_visibility="collapsed"
    )
    
    if page == "Historique":
        st.session_state.page = "history"
    elif page == "Analytics":
        st.session_state.page = "analytics"
    elif page == "Tokens OpenAI":
        st.session_state.page = "tokens"
    elif page == "Mots-clés SEO":
        st.session_state.page = "keywords"
    else:
        st.session_state.page = "create"
    
    st.markdown("---")
    
    if st.button("Recommencer", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ['page']:
                del st.session_state[key]
        st.session_state.step = 'input'
        st.rerun()
    
    st.markdown("---")
    st.markdown("### État actuel")
    current_step = st.session_state.get('step', 'input')
    st.info(f"Étape : {current_step}")
    
    if st.session_state.get('topic'):
        st.markdown(f"**Sujet :** {st.session_state.topic}")
    
    st.markdown("---")
    st.markdown("### À propos")
    st.markdown("""
    Cette interface permet de :
    - Générer des idées d'articles
    - Rédiger automatiquement
    - Optimiser le SEO
    - Publier sur Sanity
    """)

# --- AUTHENTIFICATION ---
if not st.session_state.get('authenticated', False):
    st.markdown("""
    <style>
        /* Cacher la sidebar sur la page de login */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        /* Centrer le contenu de login */
        .main .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            max-width: 100% !important;
        }
        
        /* Centrer verticalement et horizontalement */
        .main {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 0;
        }
        
        .login-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100vw;
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
        }
        
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 400px;
            width: 100%;
            margin: 0 auto;
            text-align: center;
        }
        
        .login-title {
            text-align: center;
            font-size: 2rem;
            margin-bottom: 30px;
            color: #1f77b4;
            font-weight: bold;
        }
        
        /* Centrer les éléments Streamlit dans le login-box */
        .login-box .stTextInput > div > div {
            margin: 0 auto;
        }
        
        .login-box .stTextInput label {
            text-align: center;
            display: block;
            width: 100%;
        }
        
        .login-box .stButton {
            margin: 0 auto;
        }
        
        /* Centrer les colonnes */
        .login-box [data-testid="column"] {
            text-align: center;
        }
    </style>
    <div class="login-wrapper">
        <div class="login-box">
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-title">Assistant Rédaction Blog Rounded</div>', unsafe_allow_html=True)
    
    # Centrer le champ de mot de passe
    st.markdown('<div style="text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
    password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe", key="password_input")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Centrer les boutons avec une colonne au milieu
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        login_clicked = st.button("Se connecter", type="primary", use_container_width=True, key="login_btn")
        if login_clicked:
            if password == "Rounded18!":
                st.session_state.authenticated = True
                st.rerun()  # Recharger la page pour afficher le contenu principal
            else:
                st.error("Mot de passe incorrect")
                st.session_state.login_error = True
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# Vérifier les erreurs d'import après authentification
if st.session_state.get('import_error'):
    st.error(f"❌ Erreur d'import : {st.session_state.import_error}")
    st.error("Vérifiez que tous les fichiers nécessaires sont présents dans le repository.")
    st.stop()

# Vérifier que toutes les fonctions sont chargées
if any(f is None for f in [generate_topic_variants, generate_article, optimize_seo]):
    st.error("❌ Erreur : Les fonctions nécessaires n'ont pas pu être chargées.")
    st.error("Vérifiez que le fichier scripts/generate_article.py existe et est valide.")
    st.stop()

# Titre principal
st.markdown('<div class="main-header">Assistant Rédaction Blog Rounded</div>', unsafe_allow_html=True)

# --- GESTION DE LA SUPPRESSION ---
if st.session_state.get('delete_article'):
    article_to_delete = BASE_DIR / "articles" / st.session_state.delete_article
    if article_to_delete.exists():
        try:
            article_to_delete.unlink()
            st.success(f"Article {st.session_state.delete_article} supprimé avec succès")
            del st.session_state.delete_article
            if st.session_state.get('page') == 'view_article':
                st.session_state.page = 'history'
                st.session_state.selected_article = None
            st.rerun()
        except Exception as e:
            st.error(f"Erreur lors de la suppression : {e}")
            del st.session_state.delete_article
    else:
        st.warning("Article introuvable")
        del st.session_state.delete_article

# --- PAGE CONSULTATION D'UN ARTICLE ---
if st.session_state.get('page') == 'view_article' and st.session_state.get('selected_article'):
    article_file = BASE_DIR / "articles" / st.session_state.selected_article
    if article_file.exists():
        st.header("Consultation de l'article")
        
        col_back, col_delete = st.columns([1, 1])
        with col_back:
            if st.button("Retour à l'historique", use_container_width=True):
                st.session_state.page = "history"
                st.session_state.selected_article = None
                st.rerun()
        with col_delete:
            if st.button("Supprimer cet article", type="secondary", use_container_width=True):
                try:
                    article_file.unlink()
                    st.success("Article supprimé avec succès")
                    st.session_state.page = "history"
                    st.session_state.selected_article = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de la suppression : {e}")
        
        content = article_file.read_text(encoding='utf-8')
        
        # Extraire les sections
        sections = re.split(r'\n---\n', content)
        
        for section in sections:
            if section.strip():
                st.markdown(section)
                st.markdown("---")
    else:
        st.error("Article introuvable")
        st.session_state.page = "history"
        st.session_state.selected_article = None
        st.rerun()
    
    # Arrêter ici si on est en mode consultation
    st.stop()

# --- PAGE HISTORIQUE ---
if st.session_state.get('page') == 'history':
    st.header("Historique des articles")
    
    # Charger tous les articles
    articles_dir = BASE_DIR / "articles"
    if articles_dir.exists():
        article_files = sorted(articles_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if article_files:
            st.info(f"{len(article_files)} article(s) trouvé(s)")
            
            # Recherche et filtre
            search_term = st.text_input("Rechercher un article", placeholder="Titre, slug, ou mot-clé...")
            
            # Afficher les articles
            for article_file in article_files:
                try:
                    content = article_file.read_text(encoding='utf-8')
                    
                    # Extraire les métadonnées
                    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                    slug_match = re.search(r'\*\*Slug:\*\* (.+)', content)
                    date_match = re.search(r'\*\*Généré le:\*\* (.+)', content)
                    summary_match = re.search(r'## Résumé SEO\s*\n\n(.+?)(?=\n---|\n##)', content, re.DOTALL)
                    
                    title = title_match.group(1) if title_match else article_file.stem
                    slug = slug_match.group(1).strip() if slug_match else "N/A"
                    date = date_match.group(1).strip() if date_match else "Date inconnue"
                    summary = summary_match.group(1).strip() if summary_match else "Aucun résumé"
                    
                    # Filtrer par recherche
                    if search_term:
                        search_lower = search_term.lower()
                        if (search_lower not in title.lower() and 
                            search_lower not in slug.lower() and 
                            search_lower not in summary.lower()):
                            continue
                    
                    with st.expander(f"{title}", expanded=False):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"**Slug :** `{slug}`")
                            st.markdown(f"**Date :** {date}")
                            st.markdown(f"**Résumé :** {summary}")
                        with col2:
                            if st.button("Lire", key=f"read_{article_file.name}"):
                                st.session_state.selected_article = article_file.name
                                st.session_state.page = "view_article"
                                st.rerun()
                        with col3:
                            if st.button("Supprimer", key=f"delete_{article_file.name}", type="secondary"):
                                st.session_state.delete_article = article_file.name
                                st.rerun()
                    
                except Exception as e:
                    st.warning(f"Erreur lors de la lecture de {article_file.name}: {e}")
        else:
            st.info("Aucun article trouvé dans le dossier `articles/`")
    else:
        st.warning("Le dossier `articles/` n'existe pas")
    
    # Arrêter ici si on est en mode historique
    st.stop()

# --- PAGE TOKENS OPENAI ---
if st.session_state.get('page') == 'tokens':
    st.header("📊 Historique des Tokens OpenAI")
    
    try:
        from utils.token_tracker import get_token_statistics, estimate_cost, load_token_history
        
        stats = get_token_statistics()
        history = load_token_history()
        
        if stats["total_entries"] == 0:
            st.info("Aucun historique de tokens disponible. Les tokens seront enregistrés lors de la génération d'articles.")
        else:
            # Statistiques globales
            st.subheader("📈 Statistiques Globales")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Entrées", stats["total_entries"])
            with col2:
                st.metric("Total Tokens", f"{stats['total_tokens']:,}")
            with col3:
                st.metric("Tokens Prompt", f"{stats['total_prompt_tokens']:,}")
            with col4:
                estimated_cost_val = estimate_cost(stats["total_tokens"])
                st.metric("Coût Estimé", f"${estimated_cost_val:.4f}")
            
            st.markdown("---")
            
            # Par opération
            if stats["by_operation"]:
                st.subheader("🔧 Par Opération")
                for operation, data in stats["by_operation"].items():
                    with st.expander(f"{operation} ({data['count']} appels)", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Tokens", f"{data['total_tokens']:,}")
                        with col2:
                            st.metric("Prompt Tokens", f"{data['prompt_tokens']:,}")
                        with col3:
                            st.metric("Completion Tokens", f"{data['completion_tokens']:,}")
                        st.caption(f"Coût estimé: ${estimate_cost(data['total_tokens']):.4f}")
            
            st.markdown("---")
            
            # Par modèle
            if stats["by_model"]:
                st.subheader("🤖 Par Modèle")
                for model, data in stats["by_model"].items():
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(f"{model}", f"{data['count']} appels")
                    with col2:
                        st.metric("Total Tokens", f"{data['total_tokens']:,}")
            
            st.markdown("---")
            
            # Historique récent
            st.subheader("📝 Historique Récent (10 dernières entrées)")
            if stats["recent_entries"]:
                for entry in reversed(stats["recent_entries"]):
                    with st.expander(
                        f"{entry.get('operation', 'unknown')} - {entry.get('timestamp', '')[:19]}",
                        expanded=False
                    ):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total", f"{entry.get('total_tokens', 0):,}")
                        with col2:
                            st.metric("Prompt", f"{entry.get('prompt_tokens', 0):,}")
                        with col3:
                            st.metric("Completion", f"{entry.get('completion_tokens', 0):,}")
                        
                        if entry.get("article_title"):
                            st.caption(f"Article: {entry['article_title']}")
                        if entry.get("topic"):
                            st.caption(f"Sujet: {entry['topic']}")
                        st.caption(f"Modèle: {entry.get('model', 'N/A')}")
                        st.caption(f"Coût: ${estimate_cost(entry.get('total_tokens', 0)):.6f}")
            
            st.markdown("---")
            
            # Export
            st.subheader("💾 Export")
            if st.button("Télécharger l'historique complet (JSON)", use_container_width=True):
                import json
                history_json = json.dumps(history, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Télécharger",
                    data=history_json,
                    file_name=f"token_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'historique: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    st.stop()

# --- PAGE ANALYTICS ---
if st.session_state.get('page') == 'analytics':
    st.header("📊 Analytics & Reporting")
    
    try:
        from utils.analytics import (
            get_comprehensive_stats,
            export_stats_csv,
            export_stats_json
        )
        import plotly.express as px
        import plotly.graph_objects as go
        import pandas as pd
        
        stats = get_comprehensive_stats()
        
        # Métriques principales
        st.subheader("📈 Métriques Principales")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Articles", stats["articles"]["total"])
        with col2:
            st.metric("Coût Total", f"${stats['costs']['total']:.4f}")
        with col3:
            avg_time = stats["generation"].get("avg_time_per_article_minutes", 0)
            st.metric("Temps Moyen/Article", f"{avg_time:.1f} min")
        with col4:
            avg_words = stats["publication"].get("avg_word_count", 0)
            st.metric("Mots Moyens", f"{avg_words:.0f}")
        
        st.markdown("---")
        
        # Graphique évolution des coûts
        if stats["costs"]["trends_30d"]:
            st.subheader("💰 Évolution des Coûts (30 derniers jours)")
            df_costs = pd.DataFrame(stats["costs"]["trends_30d"])
            df_costs["date"] = pd.to_datetime(df_costs["date"])
            
            fig_costs = px.line(
                df_costs,
                x="date",
                y="cost",
                title="Coûts quotidiens OpenAI",
                labels={"cost": "Coût ($)", "date": "Date"}
            )
            fig_costs.update_traces(line_color="#1f77b4", line_width=2)
            st.plotly_chart(fig_costs, use_container_width=True)
            
            # Statistiques coûts
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Coût Moyen/Jour", f"${df_costs['cost'].mean():.4f}")
            with col2:
                st.metric("Coût Max/Jour", f"${df_costs['cost'].max():.4f}")
            with col3:
                st.metric("Total 30 jours", f"${df_costs['cost'].sum():.4f}")
        
        st.markdown("---")
        
        # Statistiques de publication
        st.subheader("📝 Statistiques de Publication")
        pub_stats = stats["publication"]
        
        if pub_stats.get("monthly_count"):
            st.markdown("**Articles par mois :**")
            df_monthly = pd.DataFrame([
                {"Mois": month, "Articles": count}
                for month, count in sorted(pub_stats["monthly_count"].items())
            ])
            
            fig_monthly = px.bar(
                df_monthly,
                x="Mois",
                y="Articles",
                title="Nombre d'articles générés par mois",
                color="Articles",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mots Moyens/Article", f"{pub_stats.get('avg_word_count', 0):.0f}")
        with col2:
            st.metric("Temps Lecture Moyen", f"{pub_stats.get('avg_read_time', 0):.1f} min")
        with col3:
            st.metric("Total Mots", f"{pub_stats.get('total_words', 0):,}")
        
        st.markdown("---")
        
        # Statistiques de génération
        st.subheader("⏱️ Statistiques de Génération")
        gen_stats = stats["generation"]
        
        if gen_stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Générations", gen_stats.get("total_generations", 0))
            with col2:
                total_time_min = gen_stats.get("total_time_seconds", 0) / 60
                st.metric("Temps Total", f"{total_time_min:.1f} min")
            with col3:
                st.metric("Temps Moyen/Article", f"{gen_stats.get('avg_time_per_article_minutes', 0):.1f} min")
        
        st.markdown("---")
        
        # Articles récents
        st.subheader("📄 Articles Récents")
        if stats["articles"]["metadata"]:
            df_articles = pd.DataFrame(stats["articles"]["metadata"])
            st.dataframe(
                df_articles[["title", "word_count", "read_time", "created_at"]].head(10),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Aucun article trouvé")
        
        st.markdown("---")
        
        # Export
        st.subheader("💾 Export des Données")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = export_stats_csv(stats)
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv_data,
                file_name=f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            json_data = export_stats_json(stats)
            st.download_button(
                label="📥 Télécharger JSON",
                data=json_data,
                file_name=f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    except ImportError as e:
        st.warning(f"⚠️  Bibliothèques manquantes : {e}")
        st.info("Installez plotly et pandas : `pip install plotly pandas`")
    except Exception as e:
        st.error(f"Erreur lors du chargement des analytics: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    st.stop()

# --- PAGE GESTION MOTS-CLÉS SEO ---
if st.session_state.get('page') == 'keywords':
    st.header("🎯 Gestion des Mots-clés SEO")
    
    try:
        from utils.keywords_manager import (
            get_all_keywords_with_stats,
            add_keyword,
            update_keyword,
            delete_keyword,
            calculate_blogs_needed
        )
        
        # Section ajout de mot-clé
        with st.expander("➕ Ajouter un nouveau mot-clé", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                new_keyword = st.text_input("Mot-clé", placeholder="ex: agent vocal IA", key="new_keyword_input")
            
            with col2:
                new_volume = st.number_input("Volume de recherche", min_value=0, value=None, step=100, key="new_volume_input")
            
            with col3:
                new_complexity = st.selectbox(
                    "Complexité SEO",
                    ["", "Facile", "Moyen", "Difficile"],
                    key="new_complexity_input"
                )
            
            if st.button("Ajouter", type="primary", use_container_width=True):
                if new_keyword and new_keyword.strip():
                    add_keyword(
                        new_keyword.strip(),
                        volume=int(new_volume) if new_volume else None,
                        complexity=new_complexity if new_complexity else None
                    )
                    st.success(f"✅ Mot-clé '{new_keyword}' ajouté !")
                    st.rerun()
                else:
                    st.error("Veuillez entrer un mot-clé")
        
        st.markdown("---")
        
        # Charger tous les mots-clés avec stats
        keywords_data = get_all_keywords_with_stats()
        
        if not keywords_data:
            st.info("Aucun mot-clé configuré. Ajoutez-en un pour commencer.")
        else:
            st.subheader(f"📊 Liste des mots-clés ({len(keywords_data)})")
            
            # Filtres
            col1, col2 = st.columns(2)
            with col1:
                search_filter = st.text_input("🔍 Rechercher", placeholder="Filtrer par mot-clé...")
            with col2:
                complexity_filter = st.selectbox(
                    "Filtrer par complexité",
                    ["Tous", "Facile", "Moyen", "Difficile"]
                )
            
            # Tableau des mots-clés
            filtered_keywords = keywords_data
            if search_filter:
                filtered_keywords = [k for k in filtered_keywords if search_filter.lower() in k["keyword"].lower()]
            if complexity_filter != "Tous":
                filtered_keywords = [k for k in filtered_keywords if k.get("complexity") == complexity_filter]
            
            if filtered_keywords:
                # Afficher chaque mot-clé dans un expander
                for idx, kw_data in enumerate(filtered_keywords):
                    keyword = kw_data["keyword"]
                    volume = kw_data.get("volume")
                    complexity = kw_data.get("complexity", "Non défini")
                    blogs_needed = kw_data.get("blogs_needed")
                    total_occurrences = kw_data["total_occurrences"]
                    articles_count = kw_data["articles_count"]
                    
                    # Titre de l'expander avec stats clés
                    expander_title = f"{keyword}"
                    if volume:
                        expander_title += f" | Volume: {volume:,}"
                    if blogs_needed:
                        expander_title += f" | Blogs: {articles_count}/{blogs_needed}"
                    if total_occurrences > 0:
                        expander_title += f" | {total_occurrences} occ."
                    
                    with st.expander(expander_title, expanded=False):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Volume recherche", f"{volume:,}" if volume else "N/A")
                        
                        with col2:
                            st.metric("Complexité SEO", complexity)
                        
                        with col3:
                            st.metric("Blogs créés", articles_count)
                        
                        with col4:
                            blogs_needed_display = f"{blogs_needed}" if blogs_needed else "N/A"
                            st.metric("Blogs nécessaires", blogs_needed_display)
                        
                        st.markdown("---")
                        
                        # Occurrences
                        st.markdown(f"**Occurrences totales :** {total_occurrences}")
                        if articles_count > 0:
                            st.markdown(f"**Articles contenant ce mot-clé :** {articles_count}")
                            if kw_data.get("articles"):
                                with st.expander(f"Voir les {articles_count} article(s)", expanded=False):
                                    for article in kw_data["articles"]:
                                        st.markdown(f"• {article}")
                        
                        st.markdown("---")
                        
                        # Édition
                        st.markdown("**Modifier les métadonnées :**")
                        edit_col1, edit_col2, edit_col3 = st.columns([2, 1, 1])
                        
                        with edit_col1:
                            st.text_input("Mot-clé", value=keyword, disabled=True, key=f"edit_keyword_{idx}")
                        
                        with edit_col2:
                            updated_volume = st.number_input(
                                "Volume",
                                min_value=0,
                                value=int(volume) if volume else None,
                                step=100,
                                key=f"edit_volume_{idx}"
                            )
                        
                        with edit_col3:
                            updated_complexity = st.selectbox(
                                "Complexité",
                                ["Facile", "Moyen", "Difficile"],
                                index=["Facile", "Moyen", "Difficile"].index(complexity) if complexity in ["Facile", "Moyen", "Difficile"] else 1,
                                key=f"edit_complexity_{idx}"
                            )
                        
                        col_save, col_delete = st.columns([1, 1])
                        with col_save:
                            if st.button("💾 Sauvegarder", key=f"save_{idx}", use_container_width=True):
                                update_keyword(
                                    keyword,
                                    volume=int(updated_volume) if updated_volume else None,
                                    complexity=updated_complexity
                                )
                                st.success("✅ Métadonnées mises à jour !")
                                st.rerun()
                        
                        with col_delete:
                            if st.button("🗑️ Supprimer", key=f"delete_{idx}", type="secondary", use_container_width=True):
                                delete_keyword(keyword)
                                st.success(f"✅ Mot-clé '{keyword}' supprimé !")
                                st.rerun()
            
            else:
                st.info("Aucun mot-clé ne correspond aux filtres.")
            
            st.markdown("---")
            
            # Statistiques globales
            st.subheader("📈 Statistiques globales")
            total_volume = sum(k.get("volume", 0) or 0 for k in keywords_data)
            total_blogs_created = sum(k["articles_count"] for k in keywords_data)
            total_blogs_needed = sum(k.get("blogs_needed", 0) or 0 for k in keywords_data if k.get("blogs_needed"))
            total_occurrences = sum(k["total_occurrences"] for k in keywords_data)
            
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            with stat_col1:
                st.metric("Total mots-clés", len(keywords_data))
            with stat_col2:
                st.metric("Volume total", f"{total_volume:,}" if total_volume > 0 else "N/A")
            with stat_col3:
                st.metric("Blogs créés", total_blogs_created)
            with stat_col4:
                st.metric("Blogs nécessaires", f"{total_blogs_needed}" if total_blogs_needed > 0 else "N/A")
            
            if total_blogs_needed > 0:
                progress = min(100, int((total_blogs_created / total_blogs_needed) * 100))
                st.progress(progress / 100)
                st.caption(f"Progression : {total_blogs_created} / {total_blogs_needed} blogs ({progress}%)")
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des mots-clés: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    st.stop()

# --- ÉTAPE 1 : SAISIE DU SUJET ---
if st.session_state.step == 'input':
    st.header("Nouveau sujet d'article")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "Quel est le sujet de l'article ?",
            placeholder="Ex: L'IA pour les secrétaires médicales en 2025...",
            value=st.session_state.topic if st.session_state.topic else ""
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("Générer des idées", type="primary", use_container_width=True)
    
    if generate_btn:
        if not topic or not topic.strip():
            st.warning("⚠️ Veuillez entrer un sujet.")
        else:
            st.session_state.topic = topic.strip()
            
            # Barre de progression
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Charger les mots-clés cibles
                status_text.text("📝 Chargement des mots-clés cibles...")
                progress_bar.progress(10)
                all_keywords = load_target_keywords()
                # Sélectionner 2 à 4 mots-clés pertinents en fonction du sujet
                st.session_state.target_keywords = select_target_keywords(topic, all_keywords)
                
                # Charger les articles existants
                status_text.text("📚 Chargement des articles existants...")
                progress_bar.progress(20)
                existing_articles = load_existing_articles()
                
                # Vérification des doublons
                status_text.text("🔍 Vérification des doublons...")
                progress_bar.progress(30)
                existing_topics = get_existing_blog_topics()
                duplicate_warning = check_topic_exists(topic, existing_topics)
                
                if duplicate_warning:
                    st.warning("⚠️ Attention : Un article similaire existe déjà sur le blog.")
                
                # Recherche Web
                status_text.text("🌍 Recherche Web (Perplexity)...")
                progress_bar.progress(50)
                search_query = f"Recherche des données récentes, études de cas, statistiques 2025 sur {topic}, agents vocaux IA, secrétariat médical, cabinets médicaux, automatisation téléphonique"
                web_data = search_web_with_sources(search_query)
                st.session_state.web_results = web_data.get("content", "")
                st.session_state.web_sources = web_data.get("sources", [])
                
                # Afficher les sources trouvées
                if st.session_state.web_sources:
                    status_text.text(f"✅ {len(st.session_state.web_sources)} source(s) trouvée(s)")
                
                # Génération des variantes
                status_text.text("💡 Génération de 3 variantes de sujets...")
                progress_bar.progress(70)
                variants = generate_topic_variants(
                    topic,
                    existing_articles,
                    st.session_state.target_keywords
                )
                st.session_state.variants = variants
                
                progress_bar.progress(100)
                status_text.text("✅ Idées générées avec succès !")
                
                st.session_state.step = 'variants'
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
                import traceback
                st.code(traceback.format_exc())

# --- ÉTAPE 2 : SÉLECTION DE LA VARIANTE ---
elif st.session_state.step == 'variants':
    st.header("Choisissez un angle éditorial")
    
    st.info(f"**Sujet :** {st.session_state.topic}")
    
    # Afficher les mots-clés ciblés
    if st.session_state.get('target_keywords'):
        with st.expander(f"🎯 Mots-clés ciblés ({len(st.session_state.target_keywords)} mots-clés)", expanded=False):
            # Afficher les mots-clés par groupes
            keywords = st.session_state.target_keywords
            cols = st.columns(3)
            chunk_size = len(keywords) // 3 + 1
            for i, col in enumerate(cols):
                with col:
                    start_idx = i * chunk_size
                    end_idx = min((i + 1) * chunk_size, len(keywords))
                    for keyword in keywords[start_idx:end_idx]:
                        st.markdown(f"• {keyword}")
        st.markdown("---")
    
    # Afficher les sources trouvées avec détails
    if st.session_state.get('web_sources'):
        with st.expander(f"📚 Sources Web trouvées ({len(st.session_state.web_sources)} sources)", expanded=False):
            for idx, source in enumerate(st.session_state.web_sources, 1):
                st.markdown(f"### Source {idx}")
                
                if isinstance(source, dict):
                    # Extraire toutes les informations disponibles
                    url = source.get("url", source.get("link", ""))
                    title = source.get("title", source.get("name", ""))
                    description = source.get("description", source.get("snippet", ""))
                    domain = source.get("domain", "")
                    
                    # Afficher le titre ou le nom
                    if title:
                        st.markdown(f"**Titre :** {title}")
                    
                    # Afficher l'URL
                    if url:
                        st.markdown(f"**URL :** [{url}]({url})")
                    elif domain:
                        st.markdown(f"**Domaine :** {domain}")
                    
                    # Afficher la description si disponible
                    if description:
                        st.markdown(f"**Description :** {description}")
                    
                    # Afficher d'autres métadonnées si disponibles
                    other_keys = {k: v for k, v in source.items() 
                                 if k not in ["url", "link", "title", "name", "description", "snippet", "domain"]}
                    if other_keys:
                        st.json(other_keys)
                elif isinstance(source, str):
                    st.markdown(f"**URL :** {source}")
                
                if idx < len(st.session_state.web_sources):
                    st.markdown("---")
        st.markdown("---")
    
    if not st.session_state.variants:
        st.warning("Aucune variante disponible. Retournez à l'étape précédente.")
        if st.button("⬅️ Retour"):
            st.session_state.step = 'input'
            st.rerun()
    else:
        # Afficher les 3 variantes en colonnes
        cols = st.columns(3)
        
        for idx, variant in enumerate(st.session_state.variants):
            with cols[idx]:
                st.markdown(f'<div class="variant-card">', unsafe_allow_html=True)
                st.subheader(f"Option {idx+1}")
                st.markdown(f"**{variant.get('title', 'N/A')}**")
                st.markdown("---")
                st.caption("**Angle :**")
                st.write(variant.get('angle', 'N/A'))
                st.markdown("**Plan :**")
                outline = variant.get('outline', [])
                for p in outline:
                    st.markdown(f"• {p}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                if st.button(f"Choisir l'option {idx+1}", key=f"btn_{idx}", use_container_width=True):
                    st.session_state.chosen_variant = variant
                    st.session_state.step = 'generation'
                    st.rerun()
        
        st.markdown("---")
        if st.button("Retour", use_container_width=True):
            st.session_state.step = 'input'
            st.rerun()

# --- ÉTAPE 3 : GÉNÉRATION & REVIEW ---
elif st.session_state.step == 'generation':
    st.header("Rédaction & Validation")
    
    if not st.session_state.chosen_variant:
        st.error("Aucune variante sélectionnée.")
        if st.button("⬅️ Retour"):
            st.session_state.step = 'variants'
            st.rerun()
    else:
        # Génération de l'article si pas encore fait
        if not st.session_state.final_article:
            with st.spinner("⏳ Rédaction de l'article complet, scoring et optimisation SEO en cours..."):
                try:
                    # 1. Génération de l'article brut
                    raw_article = generate_article(
                        st.session_state.chosen_variant,
                        st.session_state.web_results,
                        st.session_state.target_keywords
                    )
                    
                    # 2. Raffinement du style
                    styled_article = apply_style_refinement(raw_article)
                    
                    # 3. Scoring initial de l'article (avant réécriture finale)
                    article_title = st.session_state.chosen_variant.get("title", st.session_state.topic)
                    scoring_before = score_article_quality(
                        styled_article,
                        st.session_state.topic,
                        st.session_state.target_keywords,
                        article_title=article_title
                    )
                    st.session_state.article_scoring_before = scoring_before
                    
                    # 4. Régénération de l'article en appliquant les recommandations de scoring
                    # Itération jusqu'à ce que le score s'améliore
                    improved_article = styled_article
                    scoring_after = None
                    score_before_value = scoring_before.get('global_score') or 0
                    max_iterations = 3
                    
                    for iteration in range(max_iterations):
                        # Régénérer l'article
                        improved_article = regenerate_article_with_scoring(
                            improved_article if iteration > 0 else styled_article,
                            scoring_before.get("markdown", "") if scoring_before else "",
                            st.session_state.topic,
                            st.session_state.target_keywords,
                        )
                        
                        # Re-scorer l'article amélioré
                        scoring_after = score_article_quality(
                            improved_article,
                            st.session_state.topic,
                            st.session_state.target_keywords,
                            article_title=article_title
                        )
                        
                        score_after_value = scoring_after.get('global_score') or 0
                        
                        # Si le score s'est amélioré, on s'arrête
                        if score_after_value > score_before_value:
                            print(f"✅ Score amélioré : {score_before_value} → {score_after_value} (itération {iteration + 1})")
                            break
                        elif iteration < max_iterations - 1:
                            # Si le score n'a pas amélioré, on réitère avec le nouveau scoring
                            print(f"⚠️  Score non amélioré ({score_after_value} vs {score_before_value}), réitération {iteration + 2}/{max_iterations}")
                            # Utiliser le nouveau scoring comme base pour la prochaine itération
                            scoring_before = scoring_after
                        else:
                            # Dernière itération, on garde quand même la version améliorée
                            print(f"⚠️  Score final : {score_after_value} (itération {iteration + 1}/{max_iterations})")
                    
                    st.session_state.article_scoring_after = scoring_after
                    
                    # 6. Optimisation SEO sur la version améliorée
                    optimized = optimize_seo(improved_article, st.session_state.target_keywords)
                    optimized["original_content"] = improved_article
                    st.session_state.final_article = optimized
                    
                    # 6.5. Analyse SEO avancée
                    try:
                        from utils.seo_analyzer import analyze_seo_comprehensive
                        seo_analysis = analyze_seo_comprehensive(
                            improved_article,
                            optimized.get("title", ""),
                            optimized.get("metaTitle", ""),
                            optimized.get("metaDescription", ""),
                            st.session_state.target_keywords or [],
                            optimized.get("focusKeyword")
                        )
                        st.session_state.seo_analysis = seo_analysis
                    except Exception as e:
                        print(f"⚠️  Erreur analyse SEO: {e}")
                        st.session_state.seo_analysis = None
                    
                    # 7. Génération version anglaise
                    english = generate_english_version(optimized)
                    st.session_state.english_article = english
                    
                    st.success("✅ Article généré avec succès !")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération : {e}")
                    import traceback
                    st.code(traceback.format_exc())
        
        # Affichage de l'article généré
        if st.session_state.final_article:
            art = st.session_state.final_article
            
            # Afficher le scoring éditorial & SEO avant/après
            if st.session_state.get('article_scoring_before') or st.session_state.get('article_scoring_after'):
                with st.expander("📊 Scoring éditorial & SEO (avant / après)", expanded=False):
                    col_score1, col_score2 = st.columns(2)
                    
                    before = st.session_state.get('article_scoring_before') or {}
                    after = st.session_state.get('article_scoring_after') or {}
                    
                    with col_score1:
                        st.markdown("**Avant amélioration**")
                        if before:
                            st.metric(
                                "Score global",
                                f"{before.get('global_score', 'N/A')}/100"
                            )
                            st.markdown(
                                f"- Contenu : {before.get('content_score', 'N/A')}/20\n"
                                f"- Lisibilité : {before.get('readability_score', 'N/A')}/20\n"
                                f"- SEO : {before.get('seo_score', 'N/A')}/30\n"
                                f"- Conversion : {before.get('conversion_score', 'N/A')}/20\n"
                                f"- Crédibilité : {before.get('credibility_score', 'N/A')}/10"
                            )
                        else:
                            st.caption("Pas de scoring initial disponible.")
                    
                    with col_score2:
                        st.markdown("**Après amélioration**")
                        if after:
                            st.metric(
                                "Score global",
                                f"{after.get('global_score', 'N/A')}/100",
                                delta=(
                                    (after.get('global_score') or 0)
                                    - (before.get('global_score') or 0)
                                    if before and after
                                    else None
                                )
                            )
                            st.markdown(
                                f"- Contenu : {after.get('content_score', 'N/A')}/20\n"
                                f"- Lisibilité : {after.get('readability_score', 'N/A')}/20\n"
                                f"- SEO : {after.get('seo_score', 'N/A')}/30\n"
                                f"- Conversion : {after.get('conversion_score', 'N/A')}/20\n"
                                f"- Crédibilité : {after.get('credibility_score', 'N/A')}/10"
                            )
                        else:
                            st.caption("Pas de scoring après amélioration disponible.")
                    
                    # Détail des rapports (utiliser des onglets au lieu d'expanders imbriqués)
                    st.markdown("---")
                    if (before and before.get("markdown")) or (after and after.get("markdown")):
                        tab_before, tab_after = st.tabs(["📝 Rapport AVANT", "📝 Rapport APRÈS"])
                        with tab_before:
                            if before and before.get("markdown"):
                                st.markdown(before["markdown"])
                            else:
                                st.info("Pas de rapport détaillé disponible pour la version avant amélioration.")
                        with tab_after:
                            if after and after.get("markdown"):
                                st.markdown(after["markdown"])
                            else:
                                st.info("Pas de rapport détaillé disponible pour la version après amélioration.")
                
                st.markdown("---")
            
            # Afficher les mots-clés utilisés dans l'article
            if st.session_state.get('target_keywords') or art.get('keywords'):
                with st.expander("🎯 Mots-clés ciblés et utilisés", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Mots-clés ciblés :**")
                        if st.session_state.get('target_keywords'):
                            st.markdown(f"*{len(st.session_state.target_keywords)} mots-clés chargés*")
                            keywords_preview = st.session_state.target_keywords[:10]
                            for keyword in keywords_preview:
                                st.markdown(f"• {keyword}")
                            if len(st.session_state.target_keywords) > 10:
                                st.caption(f"... et {len(st.session_state.target_keywords) - 10} autres")
                    
                    with col2:
                        st.markdown("**Mots-clés dans l'article :**")
                        article_keywords = art.get('keywords', [])
                        if article_keywords:
                            for keyword in article_keywords:
                                st.markdown(f"• {keyword}")
                        else:
                            st.info("Aucun mot-clé spécifique extrait")
                    
                    # Focus keyword
                    if art.get('focusKeyword'):
                        st.markdown("---")
                        st.markdown(f"**Focus Keyword :** `{art.get('focusKeyword')}`")
                st.markdown("---")
            
            # Analyse SEO avancée
            if st.session_state.get('seo_analysis'):
                try:
                    import pandas as pd
                except ImportError:
                    pd = None
                
                with st.expander("🔍 Analyse SEO Avancée", expanded=False):
                    seo_analysis = st.session_state.seo_analysis
                    
                    # Score global SEO
                    st.subheader("Score SEO Global")
                    overall_score = seo_analysis.get("overall_score", 0)
                    st.metric("Score SEO", f"{overall_score}/100")
                    
                    # Barre de progression
                    st.progress(overall_score / 100)
                    
                    st.markdown("---")
                    
                    # Densité des mots-clés
                    st.subheader("📊 Densité des Mots-clés")
                    keyword_density = seo_analysis.get("keyword_density", {})
                    if keyword_density:
                        if pd:
                            df_density = pd.DataFrame([
                                {"Mot-clé": kw, "Densité (%)": density}
                                for kw, density in keyword_density.items()
                            ])
                            st.dataframe(df_density, use_container_width=True, hide_index=True)
                        else:
                            # Affichage simple si pandas n'est pas disponible
                            for kw, density in keyword_density.items():
                                st.markdown(f"**{kw}** : {density}%")
                        
                        # Recommandations densité
                        for kw, density in keyword_density.items():
                            if density < 1.0:
                                st.warning(f"⚠️  '{kw}' : Densité trop faible ({density}%). Cible : 1-2%")
                            elif density > 2.5:
                                st.warning(f"⚠️  '{kw}' : Densité trop élevée ({density}%). Risque de sur-optimisation")
                            else:
                                st.success(f"✅ '{kw}' : Densité optimale ({density}%)")
                    else:
                        st.info("Aucune densité calculée")
                    
                    st.markdown("---")
                    
                    # Suggestions LSI
                    lsi_suggestions = seo_analysis.get("lsi_suggestions", [])
                    if lsi_suggestions:
                        st.subheader("💡 Suggestions Mots-clés LSI")
                        st.markdown("Mots-clés sémantiquement liés à intégrer :")
                        for suggestion in lsi_suggestions:
                            st.markdown(f"• {suggestion}")
                    else:
                        st.info("Aucune suggestion LSI disponible")
                    
                    st.markdown("---")
                    
                    # Lisibilité
                    st.subheader("📖 Score de Lisibilité (Flesch Reading Ease)")
                    readability = seo_analysis.get("readability", {})
                    if readability:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Score", f"{readability.get('score', 0):.1f}/100")
                        with col2:
                            st.metric("Niveau", readability.get("level", "N/A"))
                        with col3:
                            st.metric("Phrases", readability.get("sentences", 0))
                        
                        st.caption(f"Mots : {readability.get('words', 0)} | "
                                 f"Longueur moyenne phrase : {readability.get('avg_sentence_length', 0):.1f} mots")
                        
                        # Recommandation lisibilité
                        if readability.get("score", 0) < 50:
                            st.warning("⚠️  Lisibilité faible. Utilisez des phrases plus courtes et un vocabulaire plus simple.")
                        elif readability.get("score", 0) >= 60:
                            st.success("✅ Lisibilité excellente")
                    
                    st.markdown("---")
                    
                    # Longueurs optimales
                    st.subheader("📏 Longueurs Optimales")
                    lengths = seo_analysis.get("lengths", {})
                    if lengths:
                        for field_name, field_data in lengths.items():
                            field_label = {
                                "title": "Titre",
                                "meta_title": "Meta Title",
                                "meta_description": "Meta Description"
                            }.get(field_name, field_name)
                            
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                status = "✅" if field_data.get("optimal") else "⚠️"
                                st.markdown(f"**{field_label}** {status}")
                            with col2:
                                st.caption(f"{field_data.get('length', 0)} chars "
                                         f"({field_data.get('min', 0)}-{field_data.get('max', 0)} optimal)")
                                if not field_data.get("optimal"):
                                    st.caption(f"💡 {field_data.get('recommendation', '')}")
                    
                    st.markdown("---")
                    
                    # Liens internes
                    st.subheader("🔗 Liens Internes")
                    links = seo_analysis.get("links", {})
                    if links:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Liens Internes", links.get("internal_count", 0))
                        with col2:
                            st.metric("Liens Externes", links.get("external_count", 0))
                        
                        st.caption(links.get("recommendation", ""))
                        
                        if links.get("internal_links"):
                            with st.expander("Voir les liens internes", expanded=False):
                                for link in links["internal_links"]:
                                    st.markdown(f"• [{link['text']}]({link['url']})")
                    
                    st.markdown("---")
                    
                    # Structure
                    st.subheader("📐 Structure")
                    structure = seo_analysis.get("structure", {})
                    if structure:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Titres H2", structure.get("h2_count", 0))
                        with col2:
                            st.metric("Titres H3", structure.get("h3_count", 0))
                        
                        if structure.get("h2_count", 0) < 2:
                            st.warning("⚠️  Ajoutez au moins 2-3 titres H2 pour améliorer la structure")
                    
                    st.markdown("---")
                    
                    # Recommandations globales
                    recommendations = seo_analysis.get("recommendations", [])
                    if recommendations:
                        st.subheader("💡 Recommandations SEO")
                        for rec in recommendations:
                            st.markdown(f"• {rec}")
            
            # Afficher les sources utilisées avec détails
            if st.session_state.get('web_sources'):
                with st.expander(f"📚 Sources Web utilisées ({len(st.session_state.web_sources)} sources)", expanded=False):
                    for idx, source in enumerate(st.session_state.web_sources, 1):
                        st.markdown(f"### Source {idx}")
                        
                        if isinstance(source, dict):
                            # Extraire toutes les informations disponibles
                            url = source.get("url", source.get("link", ""))
                            title = source.get("title", source.get("name", ""))
                            description = source.get("description", source.get("snippet", ""))
                            domain = source.get("domain", "")
                            
                            # Afficher le titre ou le nom
                            if title:
                                st.markdown(f"**Titre :** {title}")
                            
                            # Afficher l'URL
                            if url:
                                st.markdown(f"**URL :** [{url}]({url})")
                            elif domain:
                                st.markdown(f"**Domaine :** {domain}")
                            
                            # Afficher la description si disponible
                            if description:
                                st.markdown(f"**Description :** {description}")
                            
                            # Afficher d'autres métadonnées si disponibles
                            other_keys = {k: v for k, v in source.items() 
                                         if k not in ["url", "link", "title", "name", "description", "snippet", "domain"]}
                            if other_keys:
                                st.json(other_keys)
                        elif isinstance(source, str):
                            st.markdown(f"**URL :** {source}")
                        
                        if idx < len(st.session_state.web_sources):
                            st.markdown("---")
                st.markdown("---")
            
            # Métadonnées SEO
            with st.expander("Métadonnées SEO", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Temps de lecture", art.get('readTime', 'N/A'))
                with col2:
                    st.metric("Catégorie", art.get('tag', 'N/A'))
                with col3:
                    st.metric("Focus Keyword", art.get('focusKeyword', 'N/A'))
                
                st.text_input("Meta Title", value=art.get('metaTitle', ''), disabled=True)
                st.text_area("Meta Description", value=art.get('metaDescription', ''), disabled=True)
                st.text_input("Slug", value=art.get('slug', ''), disabled=True)
                keywords = art.get('keywords', [])
                if keywords:
                    st.markdown("**Mots-clés :** " + ", ".join(keywords))
            
            # Mode édition ou visualisation
            edit_col1, edit_col2 = st.columns([1, 1])
            with edit_col1:
                if st.button("Mode Édition" if not st.session_state.edit_mode else "Mode Visualisation", 
                            use_container_width=True, type="primary" if not st.session_state.edit_mode else "secondary"):
                    st.session_state.edit_mode = not st.session_state.edit_mode
                    # Réinitialiser le contenu édité quand on change de mode
                    if not st.session_state.edit_mode:
                        st.session_state.edited_content_fr = None
                        st.session_state.edited_content_en = None
                    st.rerun()
            
            with edit_col2:
                if st.session_state.edit_mode and st.button("Appliquer les modifications", use_container_width=True, type="primary"):
                    # Appliquer les modifications
                    if st.session_state.edited_content_fr:
                        st.session_state.final_article['original_content'] = st.session_state.edited_content_fr
                        st.session_state.final_article['blog_post'] = st.session_state.edited_content_fr
                    if st.session_state.english_article and st.session_state.edited_content_en:
                        st.session_state.english_article['original_content'] = st.session_state.edited_content_en
                        st.session_state.english_article['blog_post'] = st.session_state.edited_content_en
                    st.success("Modifications appliquées !")
                    st.session_state.article_saved = False  # Réinitialiser pour sauvegarder à nouveau
                    st.rerun()
            
            st.markdown("---")
            
            # Fonction pour convertir HTML en markdown
            def html_to_markdown(html_text):
                    """Convertit le HTML en markdown basique pour l'édition"""
                    if not html_text or '<' not in html_text or '>' not in html_text:
                        return html_text
                    
                    # Conversions basiques
                    text = html_text
                    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', text, flags=re.IGNORECASE | re.DOTALL)
                    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', text, flags=re.IGNORECASE | re.DOTALL)
                    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', text, flags=re.IGNORECASE | re.DOTALL)
                    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.IGNORECASE | re.DOTALL)
                    text = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.IGNORECASE | re.DOTALL)
                    text = re.sub(r'<ul[^>]*>', '', text, flags=re.IGNORECASE)
                    text = re.sub(r'</ul>', '', text, flags=re.IGNORECASE)
                    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', text, flags=re.IGNORECASE | re.DOTALL)
                    text = re.sub(r'<[^>]+>', '', text)  # Enlever les autres balises
                    text = re.sub(r'\n{3,}', '\n\n', text)  # Nettoyer les sauts de ligne multiples
                    return text.strip()
            
            # Contenu de l'article
            tab1, tab2 = st.tabs(["Version Française", "Version Anglaise"])
            
            with tab1:
                st.subheader(art.get('title', 'Sans titre'))
                st.markdown(f"**Résumé SEO :** {art.get('summary', '')}")
                st.markdown("---")
                
                # Contenu original
                original_content = art.get('original_content', art.get('blog_post', ''))
                
                if st.session_state.edit_mode:
                    # Mode édition : text_area éditable
                    st.markdown("**Éditez le contenu (Markdown) :**")
                    
                    # Initialiser le contenu éditable si pas déjà fait
                    if st.session_state.edited_content_fr is None:
                        # Convertir HTML en markdown si nécessaire
                        if '<' in original_content and '>' in original_content:
                            st.session_state.edited_content_fr = html_to_markdown(original_content)
                        else:
                            st.session_state.edited_content_fr = original_content
                    
                    edited = st.text_area(
                        "Contenu de l'article (FR)",
                        value=st.session_state.edited_content_fr,
                        height=600,
                        label_visibility="collapsed",
                        key="editor_fr"
                    )
                    st.session_state.edited_content_fr = edited
                    
                    # Aperçu en temps réel
                    with st.expander("Aperçu en temps réel", expanded=False):
                        st.markdown(edited)
                else:
                    # Mode visualisation : affichage normal
                    if original_content:
                        # Si c'est du HTML, on l'affiche tel quel
                        if '<' in original_content and '>' in original_content:
                            st.markdown(original_content, unsafe_allow_html=True)
                        else:
                            # Sinon c'est du markdown
                            st.markdown(original_content)
            
            with tab2:
                if st.session_state.english_article:
                    en_art = st.session_state.english_article
                    st.subheader(en_art.get('title', 'No title'))
                    st.markdown(f"**SEO Summary :** {en_art.get('summary', '')}")
                    st.markdown("---")
                    
                    en_original_content = en_art.get('original_content', en_art.get('blog_post', ''))
                    
                    if st.session_state.edit_mode:
                        # Mode édition : text_area éditable
                        st.markdown("**Éditez le contenu (Markdown) :**")
                        
                        # Initialiser le contenu éditable si pas déjà fait
                        if st.session_state.edited_content_en is None:
                            # Convertir HTML en markdown si nécessaire
                            if '<' in en_original_content and '>' in en_original_content:
                                st.session_state.edited_content_en = html_to_markdown(en_original_content)
                            else:
                                st.session_state.edited_content_en = en_original_content
                        
                        edited_en = st.text_area(
                            "Contenu de l'article (EN)",
                            value=st.session_state.edited_content_en,
                            height=600,
                            label_visibility="collapsed",
                            key="editor_en"
                        )
                        st.session_state.edited_content_en = edited_en
                        
                        # Aperçu en temps réel
                        with st.expander("Aperçu en temps réel", expanded=False):
                            st.markdown(edited_en)
                    else:
                        # Mode visualisation : affichage normal
                        if en_original_content:
                            if '<' in en_original_content and '>' in en_original_content:
                                st.markdown(en_original_content, unsafe_allow_html=True)
                            else:
                                st.markdown(en_original_content)
                else:
                    st.warning("Version anglaise non générée.")
            
            # Actions
            st.markdown("---")
            st.subheader("Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Sauvegarder automatiquement si pas encore fait
                if not st.session_state.get('article_saved'):
                    try:
                        # Utiliser le contenu modifié si disponible
                        article_to_save = st.session_state.final_article.copy()
                        if st.session_state.edited_content_fr:
                            article_to_save['original_content'] = st.session_state.edited_content_fr
                            article_to_save['blog_post'] = st.session_state.edited_content_fr
                        
                        en_article_to_save = None
                        if st.session_state.english_article:
                            en_article_to_save = st.session_state.english_article.copy()
                            if st.session_state.edited_content_en:
                                en_article_to_save['original_content'] = st.session_state.edited_content_en
                                en_article_to_save['blog_post'] = st.session_state.edited_content_en
                        
                        filepath = save_article_for_review(
                            article_to_save,
                            st.session_state.chosen_variant.get('title', st.session_state.topic),
                            en_article_to_save
                        )
                        st.session_state.article_saved = True
                        st.session_state.saved_filepath = filepath.name
                        st.success(f"Sauvegardé automatiquement : `{filepath.name}`")
                    except Exception as e:
                        st.error(f"Erreur lors de la sauvegarde : {e}")
                else:
                    st.info(f"Déjà sauvegardé : `{st.session_state.get('saved_filepath', 'N/A')}`")
                    if st.button("Sauvegarder à nouveau", type="secondary", use_container_width=True):
                        try:
                            # Utiliser le contenu modifié si disponible
                            article_to_save = st.session_state.final_article.copy()
                            if st.session_state.edited_content_fr:
                                article_to_save['original_content'] = st.session_state.edited_content_fr
                                article_to_save['blog_post'] = st.session_state.edited_content_fr
                            
                            en_article_to_save = None
                            if st.session_state.english_article:
                                en_article_to_save = st.session_state.english_article.copy()
                                if st.session_state.edited_content_en:
                                    en_article_to_save['original_content'] = st.session_state.edited_content_en
                                    en_article_to_save['blog_post'] = st.session_state.edited_content_en
                            
                            filepath = save_article_for_review(
                                article_to_save,
                                st.session_state.chosen_variant.get('title', st.session_state.topic),
                                en_article_to_save
                            )
                            st.session_state.saved_filepath = filepath.name
                            st.success(f"Sauvegardé dans : `{filepath.name}`")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur : {e}")
            
            with col2:
                if st.button("Publier sur Sanity", type="primary", use_container_width=True):
                    with st.spinner("Publication en cours..."):
                        try:
                            # S'assurer que les modifications sont appliquées avant publication
                            article_to_publish = st.session_state.final_article.copy()
                            
                            # Si du contenu a été modifié, l'utiliser
                            if st.session_state.edited_content_fr:
                                article_to_publish['original_content'] = st.session_state.edited_content_fr
                                article_to_publish['blog_post'] = st.session_state.edited_content_fr
                            
                            cat_slug = article_to_publish.get("tag", "actualites-tendances")
                            refs = fetch_sanity_references(cat_slug)
                            
                            # Publication FR
                            res_fr = publish_to_production(
                                article_to_publish,
                                refs,
                                "fr"
                            )
                            
                            # Publication EN si disponible
                            res_en = False
                            if st.session_state.english_article:
                                en_article_to_publish = st.session_state.english_article.copy()
                                
                                # Si du contenu EN a été modifié, l'utiliser
                                if st.session_state.edited_content_en:
                                    en_article_to_publish['original_content'] = st.session_state.edited_content_en
                                    en_article_to_publish['blog_post'] = st.session_state.edited_content_en
                                
                                res_en = publish_to_production(
                                    en_article_to_publish,
                                    refs,
                                    "en"
                                )
                            
                            if res_fr:
                                st.success("Article français publié avec succès !")
                                if res_en:
                                    st.success("Article anglais publié avec succès !")
                                st.balloons()
                                
                                # Mettre à jour l'article dans session_state avec les modifications
                                st.session_state.final_article = article_to_publish
                                if st.session_state.english_article:
                                    st.session_state.english_article = en_article_to_publish if st.session_state.edited_content_en else st.session_state.english_article
                                
                                # Réinitialiser le flag de sauvegarde pour sauvegarder la version modifiée
                                st.session_state.article_saved = False
                            else:
                                st.error("Erreur lors de la publication FR")
                                
                        except Exception as e:
                            st.error(f"Erreur : {e}")
                            import traceback
                            st.code(traceback.format_exc())
            
            with col3:
                col3a, col3b = st.columns(2)
                with col3a:
                    if st.button("Régénérer", type="secondary", use_container_width=True):
                        st.session_state.final_article = None
                        st.session_state.english_article = None
                        st.session_state.article_saved = False
                        st.rerun()
                with col3b:
                    if st.button("Voir l'historique", type="secondary", use_container_width=True):
                        st.session_state.page = "history"
                        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "Générateur d'articles Rounded - Powered by Streamlit"
    "</div>",
    unsafe_allow_html=True
)

