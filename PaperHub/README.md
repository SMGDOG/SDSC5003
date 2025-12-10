# PaperHub - Personal Academic Paper Management and Recommendation System(个人学术论文管理与推荐系统)

An intelligent paper management system built on Python + FastAPI + PostgreSQL + Streamlit, supporting batch import of arXiv papers, semantic search, and personalized recommendations.

## 核心功能

- **批量导入**：支持从 arXiv 按关键词或分类批量导入论文
- **智能搜索**：基于标题、摘要、标签、类别等多维度搜索
- **智能推荐**：
  - 基于 sentence-transformers 的语义相似度推荐
  - 个性化推荐（基于阅读历史）
  - 混合推荐策略
- **标签管理**：多对多标签系统，灵活分类
- **统计分析**：论文分布、阅读记录等可视化统计
- **向量存储**：使用 pgvector 存储和检索 384 维语义向量

## Core Features

- **Batch Import**: Supports bulk import of papers from arXiv by keywords or categories
- **Intelligent Search**: Multi-dimensional search based on title, abstract, tags, categories, and more
- **Intelligent Recommendations**:
  - Semantic similarity recommendations based on sentence-transformers
  - Personalized recommendations (based on reading history)
  - Hybrid recommendation strategies
- **Tag Management**: Many-to-many tag system for flexible categorization
- **Statistical Analysis**: Visualized statistics on paper distribution, reading records, and more
- **Vector Storage**: Uses pgvector to store and retrieve 384-dimensional semantic vectors

## 技术栈

- **后端框架**：FastAPI
- **前端界面**：Streamlit
- **数据库**：PostgreSQL + pgvector
- **ORM**：SQLAlchemy 2.0
- **推荐引擎**：sentence-transformers (all-MiniLM-L6-v2)
- **论文数据源**：arXiv API
- **容器化**：Docker Compose

## Technology Stack

- **Backend Framework**: FastAPI
- **Frontend Interface**: Streamlit
- **Database**: PostgreSQL + pgvector
- **ORM**: SQLAlchemy 2.0
- **Recommendation Engine**: sentence-transformers (all-MiniLM-L6-v2)
- **Paper Data Source**: arXiv API
- **Containerization**: Docker Compose

## 项目结构

```
PaperHub/
│
├── app/                          # 主应用目录
│   ├── __init__.py              # Python 包初始化
|   |
│   ├── main.py                  # Streamlit 主程序
│   │
│   ├── database.py              # 数据库配置
│   │
│   ├── models.py                # ORM 模型
│   │
│   ├── schemas.py               # Pydantic 验证模型
│   │
│   ├── crud.py                  # 数据库操作
│   │
│   ├── recommender.py           # 推荐引擎
│   │
│   └── utils.py                 # 工具函数
│
├── .env                         # 环境变量（生产配置）
├── .env.example                 # 环境变量模板
├── .gitignore                   # Git 忽略规则
│
├── docker-compose.yml           # Docker 编排文件
│
├── init.sql                     # 数据库初始化 SQL
│
├── requirements.txt             # Python 依赖清单
│
├── start.bat                    # Windows 启动脚本
│
├── README.md                    # 完整项目文档
│
├── QUICKSTART.md                # 快速开始指南
│
└── PROJECT_OVERVIEW.md          # 项目概览
```

## Project Structure

```
PaperHub/
│
├── app/                          # Main application directory
│   ├── __init__.py              # Python package initialization
|   |  
│   ├── main.py                  # Streamlit main program
│   │
│   ├── database.py              # Database configuration
│   │
│   ├── models.py                # ORM models
│   │
│   ├── schemas.py               # Pydantic validation models
│   │
│   ├── crud.py                  # Database operations
│   │
│   ├── recommender.py           # Recommendation engine
│   │
│   └── utils.py                 # Utility functions
│
├── .env                         # Environment variables (production configuration)
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
│
├── docker-compose.yml           # Docker orchestration file
│
├── init.sql                     # Database initialization SQL
│
├── requirements.txt             # Python dependency list
│
├── start.bat                    # Windows startup script
│
├── README.md                    # Complete project documentation
│
├── QUICKSTART.md                # Quick start guide
│
└── PROJECT_OVERVIEW.md          # Project overview
```

## Quick Start

### 1. Environment Preparation

Ensure the following software is installed：
- Python 3.9+
- Docker Desktop
- Git

### 2. Clone the project

```bash
git clone <your-repo-url>
cd PaperHub
```

### 3. Configure environment variables

```bash
copy .env.example .env
```

`.env` Examples of file contents：
```env
DATABASE_URL=postgresql://paperhub:paperhub123@localhost:5432/paperhub
POSTGRES_USER=paperhub
POSTGRES_PASSWORD=paperhub123
POSTGRES_DB=paperhub
```

### 4. Start the database

Start PostgreSQL (with pgvector extension) using Docker Compose:

```bash
docker-compose up -d
```

Wait for the database to start (approximately 10-20 seconds). 
You can check the status with the following command:

```bash
docker-compose ps
```

### 5. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 6. Initialize the database

```bash
python -m app.database
```

you can see：`数据库表创建成功！`

### 7. Start the application

```bash
python -m streamlit run app/main.py
```

## User Guide

### Import Papers

1. Navigate to the **📥 Import Papers** page
2. Select an import method:
   - **Keyword Search**: Enter keywords (e.g., "deep learning") to search arXiv
   - **Category Browsing**: Select arXiv categories (e.g., cs.AI, cs.CV) to retrieve papers in bulk
3. Click **➕ Import** to add papers to the database (embeddings are generated automatically)

### Browse and Search

1. View all papers on the **🏠 Home** page
2. Use the search box to enter keywords (searches titles and abstracts)
3. Filter by categories and tags
4. Enable date filtering to view papers from a specific time range

### Intelligent Recommendations

1. When viewing **paper details**, the system automatically recommends similar papers
2. Navigate to the **🎯 Recommendations** page:
   - **Based on Reading History**: Get recommendations related to papers you've read
   - **Based on Current Paper**: Select a paper to find similar research

### Tag Management

1. Navigate to the **🏷️ Tag Management** page
2. Create new tags or view existing ones
3. Check the number of papers associated with each tag

### Statistics

Navigate to the **📊 Statistics page** to view:
- Total number of papers, tags, and read papers
- Distribution of papers across categories
- Recently imported papers

## Database Models

### Paper
- `id`: Primary Key
- `title`: title of paper
- `authors`: list of authors（JSON）
- `abstract`: abstract
- `pdf_url`: PDF download link
- `arxiv_id`: arXiv ID
- `category`: category
- `published_date`: published date
- `embedding`: 384-dimensional semantic vector（pgvector）

### Tag
- `id`: Primary Key
- `name`: name of tag
- `description`: description

### PaperTag
- n to m

### ReadingHistory
- `id`: Primary Key
- `paper_id`: ID of paper
- `user_id`: ID of user
- `read_at`: time of reading
- `rating`: (1 to 5)
- `notes`: notes

## Recommendation Algorithm

### 1. Content-Based Recommendation

using `sentence-transformers/all-MiniLM-L6-v2` model：
- input：title and abstract
- output：384-dimensional semantic vector
- Similarity calculation: Cosine similarity (pgvector <=> operator)

### 2. Reading History-Based Recommendation

- Retrieve the N most recently read papers by the user
- Calculate the average embedding of these papers
- Find papers most similar to the average vector (excluding those already read)

### 3. Hybrid Recommendation

- Combine current paper and user history:
- Current paper embedding: 70%
- Historical average embedding: 30%

## Configuration Instructions

### Environment Variables

| Variables | Description | Default Value |
|--------|------|--------|
| `DATABASE_URL` | PostgreSQL linking URL | `postgresql://postgres:123456@localhost:5432/postgres` |
| `EMBEDDING_MODEL` | sentence-transformers model name | `sentence-transformers/all-MiniLM-L6-v2` |
| `EMBEDDING_DIMENSION` | dimensional semantic vector | `384` |
| `ARXIV_MAX_RESULTS` | the max number of arXiv search | `50` |

### Database configuration

Default configuration (can be modified in docker-compose.yml):
- user：`paperhub`
- password：`paperhub123`
- DB：`paperhub`
- localhost：`5432`

## Extension Suggestions

- [ ] User Authentication System (Supports Multiple Users)
- [ ] PDF Text Extraction and Full-Text Search
- [ ] Notes and Annotation Features
- [ ] Paper Citation Relationship Graph
- [ ] Email Subscription (Regular Recommendations)
- [ ] RESTful API（FastAPI）
- [ ] Export Functionality (BibTeX, Markdown)
