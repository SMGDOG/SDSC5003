# PaperHub Project Overview

## Project Introduction

PaperHub - Personal Academic Paper Management and Recommendation System

### Core Values

- **One-stop management**: Centrally manage all papers, eliminating folder clutter
- **Intelligent recommendation**：Automatically recommend related papers based on AI semantic understanding
- **Bulk import**：One-click import of the latest research from arXiv
- **Multi-dimensional search**：Quickly locate by title, author, category, and tags

## Technical Architecture

```
┌──────────────────────────────────────────────────────────┐
│         Streamlit Web UI (Frontend)                      │
│  - Paper list  - Detail page  - Recommendations - Import │
└─────────────────────────┬────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────┐
│         Python Business Logic Layer                        │
│  - CRUD operations  - Recommendation engine  - Web crawler │
└─────────────────────────┬──────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────┐
│     PostgreSQL + pgvector (Data Layer)             │
│  - Paper data  - Vector indexes  - Relational data │
└────────────────────────────────────────────────────┘
```

## Core Components

### 1. Database Layer (database.py, models.py)

**Data Models**：
- `Paper`: Main paper table (with 384-dimensional vectors)
- `Tag`: Tag table
- `PaperTag`: Many-to-many association table
- `ReadingHistory`: Reading history

### 2. CRUD Layer (crud.py)

**Core Functions**：
- Paper creation, deletion, update, and query (supporting multi-condition filtering)
- Tag management
- Reading history recording
- Statistical queries

### 3. Recommendation Engine (recommender.py)

**Recommendation Strategies**：
- **Content-based**: Calculate paper embedding similarity, When viewing paper details
- **History-based**: Analyze user reading habits, Personalized recommendations
- **Hybrid recommendation**: 70% current paper + 30% history, Balance exploration and exploitation

**Model**：
- sentence-transformers/all-MiniLM-L6-v2
- 384-dimensional vectors
- Cosine similarity calculation

### 4. Crawler Tools (utils.py)

**arXiv Integration**：
- Keyword search
- Category browsing
- Single paper retrieval
- Automatic parsing (title, authors, abstract, etc.)

### 5. User Interface (main.py)

**6 Main Pages**：
1. **🏠 Home**：Paper list + search + filtering
2. **📄 Paper Details**：Complete information + similar recommendations
3. **🎯 Recommendations**：Personalized + content-based
4. **📥 Import Papers**：arXiv search + import
5. **🏷️ Tag Management**：Create + view + delete
6. **📊 Statistics**：Data overview + visualization
