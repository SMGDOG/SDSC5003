"""
PaperHub - Personal Academic Paper Management and Recommendation System
Streamlit Main Application
"""
import streamlit as st
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd

from app.database import SessionLocal, init_db
from app.models import Paper, Tag
from app import crud
from app.schemas import PaperCreate, TagCreate, ReadingHistoryCreate
from app.recommender import recommender
from app.utils import (
    search_arxiv_papers,
    fetch_arxiv_by_id,
    format_authors,
    truncate_text,
    get_arxiv_categories,
    extract_arxiv_id
)


# ==================== Configuration ====================

st.set_page_config(
    page_title="PaperHub - Academic Paper Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== Database Session Management ====================

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Close at page end


# ==================== Sidebar Navigation ====================

def render_sidebar():
    """Render sidebar"""
    with st.sidebar:
        st.title("📚 PaperHub")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["🏠 Home", "📄 Paper Details", "🎯 Recommendations", "📥 Import Papers", "🏷️ Tag Management", "📊 Statistics"],
            key="navigation"
        )
        
        st.markdown("---")
        st.markdown("### Quick Actions")
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        return page


# ==================== Home: Paper List ====================

def render_home_page(db: Session):
    """Render home page"""
    st.title("🏠 Paper Library")
    
    # Search and filter area
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search Papers (Title/Abstract)", placeholder="Enter keywords...")
    
    with col2:
        categories = crud.get_categories(db)
        category_filter = st.selectbox(
            "Category Filter",
            ["All"] + categories
        )
    
    with col3:
        tags = crud.get_tags(db)
        tag_options = {tag.name: tag.id for tag in tags}
        selected_tags = st.multiselect("Tag Filter", options=list(tag_options.keys()))
    
    # Date range filter
    col4, col5 = st.columns(2)
    with col4:
        use_date_filter = st.checkbox("Enable Date Filter")
    
    start_date, end_date = None, None
    if use_date_filter:
        with col5:
            date_range = st.date_input(
                "Publication Date Range",
                value=(datetime.now() - timedelta(days=365), datetime.now()),
                max_value=datetime.now()
            )
            if len(date_range) == 2:
                start_date, end_date = date_range
    
    # Query papers
    tag_ids = [tag_options[name] for name in selected_tags] if selected_tags else None
    category = None if category_filter == "All" else category_filter
    
    papers = crud.get_papers(
        db,
        query=search_query if search_query else None,
        category=category,
        tag_ids=tag_ids,
        start_date=start_date,
        end_date=end_date,
        limit=50
    )
    
    # Display statistics
    st.markdown(f"**Found {len(papers)} papers**")
    
    # Display paper list
    if papers:
        for paper in papers:
            render_paper_card(db, paper)
    else:
        st.info("No papers yet. Please import data first.")


def render_paper_card(db: Session, paper: Paper):
    """Render paper card"""
    with st.container():
        col1, col2 = st.columns([5, 1])
        
        with col1:
            # Title (clickable for details)
            if st.button(f"📄 {paper.title}", key=f"title_{paper.id}", use_container_width=True):
                st.session_state.selected_paper_id = paper.id
                st.session_state.nav_request = "📄 Paper Details"
                st.rerun()
            
            # Authors and date
            author_str = format_authors(paper.authors, max_display=3)
            date_str = paper.published_date.strftime("%Y-%m-%d") if paper.published_date else "Unknown"
            st.caption(f"👤 {author_str} | 📅 {date_str} | 🏷️ {paper.category or 'N/A'}")
            
            # Abstract
            if paper.abstract:
                st.text(truncate_text(paper.abstract, max_length=200))
            
            # Tags
            paper_tags = [pt.tag.name for pt in paper.paper_tags]
            if paper_tags:
                st.markdown(" ".join([f"`{tag}`" for tag in paper_tags]))
        
        with col2:
            if paper.pdf_url:
                st.link_button("📥 PDF", paper.pdf_url, use_container_width=True)
            
            if st.button("✅ Mark as Read", key=f"read_{paper.id}", use_container_width=True):
                crud.create_reading_history(
                    db,
                    ReadingHistoryCreate(paper_id=paper.id, user_id="default_user")
                )
                st.success("Marked as read!")
                st.rerun()
        
        st.markdown("---")


# ==================== Paper Detail Page ====================

def render_paper_detail_page(db: Session):
    """Render paper detail page"""
    st.title("📄 Paper Details")
    
    paper_id = st.session_state.get("selected_paper_id")
    
    if not paper_id:
        st.warning("Please select a paper from the home page first")
        return
    
    paper = crud.get_paper(db, paper_id)
    
    if not paper:
        st.error("Paper does not exist")
        return
    
    # Basic information
    st.header(paper.title)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**Authors:** {format_authors(paper.authors, max_display=10)}")
        st.markdown(f"**Category:** {paper.category or 'N/A'}")
        st.markdown(f"**Published Date:** {paper.published_date.strftime('%Y-%m-%d') if paper.published_date else 'Unknown'}")
        
        if paper.arxiv_id:
            st.markdown(f"**arXiv ID:** [{paper.arxiv_id}](https://arxiv.org/abs/{paper.arxiv_id})")
    
    with col2:
        if paper.pdf_url:
            st.link_button("📥 Download PDF", paper.pdf_url, use_container_width=True)
        
        if st.button("✅ Mark as Read", use_container_width=True):
            crud.create_reading_history(
                db,
                ReadingHistoryCreate(paper_id=paper.id, user_id="default_user")
            )
            st.success("Marked as read!")
    
    # Tags
    st.markdown("---")
    st.markdown("### 🏷️ Tags")
    
    # Display current tags
    paper_tags = [pt.tag for pt in paper.paper_tags]
    current_tag_names = [tag.name for tag in paper_tags]
    
    if current_tag_names:
        st.markdown("**Current Tags:**")
        cols = st.columns(len(current_tag_names) + 1)
        for idx, tag in enumerate(paper_tags):
            with cols[idx]:
                if st.button(f"❌ {tag.name}", key=f"remove_tag_{tag.id}", use_container_width=True):
                    # Remove tag from paper
                    from app.models import PaperTag
                    paper_tag = db.query(PaperTag).filter(
                        PaperTag.paper_id == paper.id,
                        PaperTag.tag_id == tag.id
                    ).first()
                    if paper_tag:
                        db.delete(paper_tag)
                        db.commit()
                        st.success(f"Tag '{tag.name}' removed!")
                        st.rerun()
    else:
        st.info("No tags yet")
    
    # Add new tag
    st.markdown("**Add Tag:**")
    all_tags = crud.get_tags(db)
    available_tags = [tag for tag in all_tags if tag.name not in current_tag_names]
    
    if available_tags:
        col1, col2 = st.columns([3, 1])
        with col1:
            tag_to_add = st.selectbox(
                "Select a tag to add",
                options=[tag.name for tag in available_tags],
                key="tag_selector"
            )
        with col2:
            st.write("")
            if st.button("➕ Add Tag", use_container_width=True):
                # Find tag by name
                tag = next((t for t in available_tags if t.name == tag_to_add), None)
                if tag:
                    from app.models import PaperTag
                    paper_tag = PaperTag(paper_id=paper.id, tag_id=tag.id)
                    db.add(paper_tag)
                    db.commit()
                    st.success(f"Tag '{tag.name}' added!")
                    st.rerun()
    else:
        st.caption("All available tags are already added to this paper")
    
    # Abstract
    st.markdown("---")
    st.markdown("### Abstract")
    if paper.abstract:
        st.write(paper.abstract)
    else:
        st.info("No abstract available")
    
    # Similar paper recommendations
    st.markdown("---")
    st.markdown("### 🎯 Similar Paper Recommendations")
    
    if paper.embedding is None:
        if st.button("Generate Recommendations (Generate embedding first)"):
            with st.spinner("Generating embedding..."):
                embedding = recommender.generate_paper_embedding(paper)
                crud.update_paper_embedding(db, paper.id, embedding)
                st.success("Embedding generated!")
                st.rerun()
    else:
        similar_papers = recommender.recommend_by_paper(db, paper.id, limit=5)
        
        if similar_papers:
            for similar_paper, score in similar_papers:
                with st.container():
                    st.markdown(f"**Similarity: {score:.2%}**")
                    if st.button(
                        f"📄 {similar_paper.title}",
                        key=f"similar_{similar_paper.id}",
                        use_container_width=True
                    ):
                        st.session_state.selected_paper_id = similar_paper.id
                        st.rerun()
                    
                    st.caption(f"👤 {format_authors(similar_paper.authors, 2)} | 🏷️ {similar_paper.category or 'N/A'}")
                    st.markdown("---")
        else:
            st.info("No similar papers found")


# ==================== Recommendation Page ====================

def render_recommendation_page(db: Session):
    """Render recommendation page"""
    st.title("🎯 Smart Recommendations")
    
    tab1, tab2 = st.tabs(["📚 Based on Reading History", "🔍 Based on Current Paper"])
    
    with tab1:
        st.markdown("### History-Based")
        
        # Display reading history
        reading_histories = crud.get_reading_histories(db, user_id="default_user", limit=10)
        
        if reading_histories:
            st.markdown(f"**You have read {len(reading_histories)} papers**")
            
            with st.expander("View Reading History"):
                for history in reading_histories:
                    st.markdown(f"- {history.paper.title} ({history.read_at.strftime('%Y-%m-%d %H:%M')})")
            
            # Generate recommendations
            if st.button("🎯 Generate Personalized Recommendations", use_container_width=True):
                with st.spinner("Analyzing your reading preferences..."):
                    recommendations = recommender.recommend_by_reading_history(
                        db,
                        user_id="default_user",
                        limit=10
                    )
                    # Save recommendations to session_state
                    st.session_state.history_recommendations = recommendations
            
            # Display recommendations from session_state
            if "history_recommendations" in st.session_state:
                recommendations = st.session_state.history_recommendations
                if recommendations:
                    st.success(f"Found {len(recommendations)} recommended papers for you!")
                    
                    for paper, score in recommendations:
                        with st.container():
                            st.markdown(f"**Match Score: {score:.2%}**")
                            if st.button(
                                f"📄 {paper.title}",
                                key=f"rec_history_{paper.id}",
                                use_container_width=True
                            ):
                                st.session_state.selected_paper_id = paper.id
                                st.session_state.nav_request = "📄 Paper Details"
                                st.rerun()
                            
                            st.caption(f"👤 {format_authors(paper.authors, 2)} | 🏷️ {paper.category or 'N/A'}")
                            if paper.abstract:
                                st.text(truncate_text(paper.abstract, 150))
                            st.markdown("---")
                else:
                    st.warning("Cannot generate recommendations yet. Please ensure papers have embeddings.")
        else:
            st.info("You don't have any reading history yet. Go to the home page and mark some papers!")
    
    with tab2:
        st.markdown("### Recommendations Based on Specific Paper")
        
        # Select paper
        papers = crud.get_papers(db, limit=100)
        paper_options = {f"{p.title[:50]}...": p.id for p in papers}
        
        if paper_options:
            selected_title = st.selectbox("Select a paper", options=list(paper_options.keys()))
            selected_id = paper_options[selected_title]
            
            if st.button("🎯 Find Similar Papers", use_container_width=True):
                paper = crud.get_paper(db, selected_id)
                
                if paper.embedding is None:
                    with st.spinner("Generating embedding..."):
                        embedding = recommender.generate_paper_embedding(paper)
                        crud.update_paper_embedding(db, paper.id, embedding)
                
                with st.spinner("Searching for similar papers..."):
                    similar_papers = recommender.recommend_by_paper(db, selected_id, limit=10)
                    # Save to session_state
                    st.session_state.paper_recommendations = similar_papers
            
            # Display recommendations from session_state
            if "paper_recommendations" in st.session_state:
                similar_papers = st.session_state.paper_recommendations
                if similar_papers:
                    st.success(f"Found {len(similar_papers)} similar papers!")
                    
                    for paper, score in similar_papers:
                        with st.container():
                            st.markdown(f"**Similarity: {score:.2%}**")
                            if st.button(
                                f"📄 {paper.title}",
                                key=f"rec_paper_{paper.id}",
                                use_container_width=True
                            ):
                                st.session_state.selected_paper_id = paper.id
                                st.session_state.nav_request = "📄 Paper Details"
                                st.rerun()
                            
                            st.caption(f"👤 {format_authors(paper.authors, 2)} | 🏷️ {paper.category or 'N/A'}")
                            if paper.abstract:
                                st.text(truncate_text(paper.abstract, 150))
                            st.markdown("---")
                else:
                    st.warning("No similar papers found")
        else:
            st.info("No paper data available")


# ==================== Import Papers Page ====================

def render_import_page(db: Session):
    """Render import papers page"""
    st.title("📥 Import Papers from arXiv")
    
    tab1, tab2 = st.tabs(["🔍 Keyword Search", "🏷️ Browse by Category"])
    
    with tab1:
        st.markdown("### Search arXiv by Keywords")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_input(
                "Search Query",
                placeholder="e.g.: machine learning, deep learning, NLP...",
                help="Supports boolean operators: AND, OR, NOT"
            )
        
        with col2:
            max_results = st.number_input("Max Results", min_value=1, max_value=100, value=10)
        
        if st.button("🔍 Search", use_container_width=True):
            if query:
                with st.spinner(f"Searching arXiv..."):
                    arxiv_papers = search_arxiv_papers(query, max_results=max_results)
                    st.session_state.arxiv_results = arxiv_papers
                    st.success(f"Found {len(arxiv_papers)} papers!")
            else:
                st.warning("Please enter a search query")
        
        # Display search results
        if 'arxiv_results' in st.session_state and st.session_state.arxiv_results:
            st.markdown("---")
            st.markdown("### Search Results")
            
            for idx, paper_data in enumerate(st.session_state.arxiv_results):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"**{paper_data['title']}**")
                        st.caption(
                            f"👤 {format_authors(paper_data['authors'], 2)} | "
                            f"📅 {paper_data['published_date'].strftime('%Y-%m-%d')} | "
                            f"🏷️ {paper_data['category']}"
                        )
                        st.text(truncate_text(paper_data['abstract'], 150))
                    
                    with col2:
                        # Check if already exists
                        existing = crud.get_paper_by_arxiv_id(db, paper_data['arxiv_id'])
                        
                        if existing:
                            st.success("✅ Imported")
                        else:
                            if st.button("➕ Import", key=f"import_{idx}", use_container_width=True):
                                import_paper_from_arxiv(db, paper_data)
                                st.rerun()
                    
                    st.markdown("---")
    
    with tab2:
        st.markdown("### Browse arXiv by Category")
        
        categories = get_arxiv_categories()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_category = st.selectbox(
                "Select Category",
                options=list(categories.keys()),
                format_func=lambda x: f"{x} - {categories[x]}"
            )
        
        with col2:
            max_results_cat = st.number_input(
                "Max Results",
                min_value=1,
                max_value=100,
                value=20,
                key="max_results_cat"
            )
        
        if st.button("🔍 Fetch Papers", use_container_width=True, key="fetch_by_category"):
            with st.spinner(f"Fetching papers from {selected_category} category..."):
                from app.utils import search_arxiv_by_category
                arxiv_papers = search_arxiv_by_category(selected_category, max_results=max_results_cat)
                st.session_state.arxiv_category_results = arxiv_papers
                st.success(f"Found {len(arxiv_papers)} papers!")
        
        # Display results
        if 'arxiv_category_results' in st.session_state and st.session_state.arxiv_category_results:
            st.markdown("---")
            
            if st.button("📥 Import All", use_container_width=True):
                with st.spinner("Importing in batch..."):
                    imported_count = 0
                    for paper_data in st.session_state.arxiv_category_results:
                        existing = crud.get_paper_by_arxiv_id(db, paper_data['arxiv_id'])
                        if not existing:
                            import_paper_from_arxiv(db, paper_data)
                            imported_count += 1
                    
                    st.success(f"Successfully imported {imported_count} papers!")
                    st.session_state.arxiv_category_results = []
                    st.rerun()
            
            st.markdown("---")
            
            for idx, paper_data in enumerate(st.session_state.arxiv_category_results):
                with st.container():
                    st.markdown(f"**{paper_data['title']}**")
                    st.caption(
                        f"👤 {format_authors(paper_data['authors'], 2)} | "
                        f"📅 {paper_data['published_date'].strftime('%Y-%m-%d')}"
                    )
                    st.markdown("---")


def import_paper_from_arxiv(db: Session, paper_data: dict):
    """Import paper from arXiv data"""
    # Create paper
    paper_create = PaperCreate(
        title=paper_data['title'],
        authors=paper_data['authors'],
        abstract=paper_data['abstract'],
        pdf_url=paper_data['pdf_url'],
        arxiv_id=paper_data['arxiv_id'],
        category=paper_data['category'],
        published_date=paper_data['published_date']
    )
    
    # Generate embedding
    with st.spinner("Generating embedding..."):
        text = f"{paper_data['title']} {paper_data['abstract'][:500]}"
        embedding = recommender.generate_embedding(text)
    
    # Create paper
    paper = crud.create_paper(db, paper_create, embedding=embedding)
    
    # Auto create tags
    if paper_data['category']:
        tag = crud.get_or_create_tag(db, paper_data['category'])
        from app.models import PaperTag
        paper_tag = PaperTag(paper_id=paper.id, tag_id=tag.id)
        db.add(paper_tag)
        db.commit()
    
    st.success(f"✅ Successfully imported: {paper_data['title'][:50]}...")


# ==================== Tag Management Page ====================

def render_tag_management_page(db: Session):
    """Render tag management page"""
    st.title("🏷️ Tag Management")
    
    # Create new tag
    with st.expander("➕ Create New Tag"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            tag_name = st.text_input("Tag Name")
            tag_desc = st.text_input("Tag Description (Optional)")
        
        with col2:
            st.write("")
            st.write("")
            if st.button("Create", use_container_width=True):
                if tag_name:
                    existing = crud.get_tag_by_name(db, tag_name)
                    if existing:
                        st.error("Tag already exists!")
                    else:
                        crud.create_tag(db, TagCreate(name=tag_name, description=tag_desc))
                        st.success(f"Tag '{tag_name}' created successfully!")
                        st.rerun()
                else:
                    st.warning("Please enter a tag name")
    
    # Display all tags
    st.markdown("---")
    st.markdown("### All Tags")
    
    tags = crud.get_tags(db, limit=100)
    
    if tags:
        for tag in tags:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{tag.name}**")
                if tag.description:
                    st.caption(tag.description)
            
            with col2:
                # Count papers using this tag
                paper_count = db.query(Paper).join(
                    Paper.paper_tags
                ).filter(
                    Paper.paper_tags.any(tag_id=tag.id)
                ).count()
                st.metric("Papers", paper_count)
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_tag_{tag.id}"):
                    crud.delete_tag(db, tag.id)
                    st.success(f"Tag '{tag.name}' deleted")
                    st.rerun()
            
            st.markdown("---")
    else:
        st.info("No tags yet")


# ==================== Statistics Page ====================

def render_statistics_page(db: Session):
    """Render statistics page"""
    st.title("📊 Statistics")
    
    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        paper_count = crud.get_paper_count(db)
        st.metric("📄 Total Papers", paper_count)
    
    with col2:
        tag_count = crud.get_tag_count(db)
        st.metric("🏷️ Tags", tag_count)
    
    with col3:
        reading_count = db.query(crud.ReadingHistory).count()
        st.metric("✅ Read Papers", reading_count)
    
    with col4:
        categories = crud.get_categories(db)
        st.metric("📂 Categories", len(categories))
    
    st.markdown("---")
    
    # Statistics by category
    st.markdown("### 📂 Statistics by Category")
    
    category_stats = []
    for category in categories:
        count = db.query(Paper).filter(Paper.category == category).count()
        category_stats.append({"Category": category, "Papers": count})
    
    if category_stats:
        df = pd.DataFrame(category_stats)
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("Category"))
    
    st.markdown("---")
    
    # Recently imported
    st.markdown("### 📅 Recently Imported Papers")
    
    recent_papers = crud.get_papers(db, limit=10)
    if recent_papers:
        for paper in recent_papers:
            st.markdown(
                f"- **{paper.title}** "
                f"({paper.created_at.strftime('%Y-%m-%d %H:%M')})"
            )
    else:
        st.info("No papers yet")


# ==================== Main Function ====================

def main():
    """Main function"""
    # Initialize database
    try:
        init_db()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        st.stop()
    
    # Get database session
    db = get_db()
    
    # Check if there's a navigation request (override sidebar selection)
    if "nav_request" in st.session_state:
        # Update the navigation radio button state
        st.session_state.navigation = st.session_state.nav_request
        del st.session_state.nav_request
    
    # Render sidebar and get page selection
    page = render_sidebar()
    
    # Render different pages based on selection
    if page == "🏠 Home":
        render_home_page(db)
    elif page == "📄 Paper Details":
        render_paper_detail_page(db)
    elif page == "🎯 Recommendations":
        render_recommendation_page(db)
    elif page == "📥 Import Papers":
        render_import_page(db)
    elif page == "🏷️ Tag Management":
        render_tag_management_page(db)
    elif page == "📊 Statistics":
        render_statistics_page(db)
    
    # Close database session
    db.close()


if __name__ == "__main__":
    main()
