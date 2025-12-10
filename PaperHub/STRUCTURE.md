# Project Structure

```
PaperHub/
│
├── app/                          # 主应用目录
│   ├── __init__.py              # Python 包初始化
│   ├── main.py                  # Streamlit 主程序
│   │                            # - 6 个功能页面
│   │                            # - UI 渲染逻辑
│   │
│   ├── database.py              # 数据库配置
│   │                            # - SQLAlchemy 引擎
│   │                            # - 会话管理
│   │                            # - 初始化函数
│   │
│   ├── models.py                # ORM 模型
│   │                            # - Paper (论文表)
│   │                            # - Tag (标签表)
│   │                            # - PaperTag (关联表)
│   │                            # - ReadingHistory (阅读历史)
│   │
│   ├── schemas.py               # Pydantic 验证模型
│   │                            # - 请求/响应数据结构
│   │                            # - 数据验证规则
│   │
│   ├── crud.py                  # 数据库操作
│   │                            # - 增删改查函数
│   │                            # - 复杂查询逻辑
│   │                            # - 统计函数
│   │
│   ├── recommender.py           # 推荐引擎
│   │                            # - sentence-transformers 集成
│   │                            # - 相似度搜索
│   │                            # - 多种推荐策略
│   │
│   └── utils.py                 # 工具函数
│                                # - arXiv API 集成
│                                # - 文本处理
│                                # - 辅助函数
│
├── .env                         # 环境变量（生产配置）
├── .env.example                 # 环境变量模板
├── .gitignore                   # Git 忽略规则
│
├── docker-compose.yml           # Docker 编排文件
│                                # - PostgreSQL + pgvector 配置
│
├── init.sql                     # 数据库初始化 SQL
│                                # - 启用 pgvector 扩展
│
├── requirements.txt             # Python 依赖清单
│                                # - 15 个核心包及版本
│
├── start.bat                    # Windows 启动脚本
│                                # - 自动化启动流程
│
├── README.md                    # 完整项目文档
│                                # - 功能介绍
│                                # - 安装指南
│                                # - 使用说明
│
├── QUICKSTART.md                # 快速开始指南
│                                # - 简化版启动步骤
│                                # - 常见问题
│
└── PROJECT_OVERVIEW.md          # 项目概览
                                 # - 架构设计
                                 # - 技术细节
                                 # - 扩展方向
```

```
PaperHub/
│
├── app/                          # Main application directory
│   ├── __init__.py              # Python package initialization
│   ├── main.py                  # Streamlit main program
│   │                            # - 6 functional pages
│   │                            # - UI rendering logic
│   │
│   ├── database.py              # Database configuration
│   │                            # - SQLAlchemy engine
│   │                            # - Session management
│   │                            # - Initialization functions
│   │
│   ├── models.py                # ORM models
│   │                            # - Paper (paper table)
│   │                            # - Tag (tag table)
│   │                            # - PaperTag (association table)
│   │                            # - ReadingHistory (reading history)
│   │
│   ├── schemas.py               # Pydantic validation models
│   │                            # - Request/response data structures
│   │                            # - Data validation rules
│   │
│   ├── crud.py                  # Database operations
│   │                            # - CRUD functions
│   │                            # - Complex query logic
│   │                            # - Statistical functions
│   │
│   ├── recommender.py           # Recommendation engine
│   │                            # - sentence-transformers integration
│   │                            # - Similarity search
│   │                            # - Multiple recommendation strategies
│   │
│   └── utils.py                 # Utility functions
│                                # - arXiv API integration
│                                # - Text processing
│                                # - Helper functions
│
├── .env                         # Environment variables (production configuration)
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
│
├── docker-compose.yml           # Docker orchestration file
│                                # - PostgreSQL + pgvector configuration
│
├── init.sql                     # Database initialization SQL
│                                # - Enable pgvector extension
│
├── requirements.txt             # Python dependency list
│                                # - 15 core packages and versions
│
├── start.bat                    # Windows startup script
│                                # - Automated startup process
│
├── README.md                    # Complete project documentation
│                                # - Feature introduction
│                                # - Installation guide
│                                # - Usage instructions
│
├── QUICKSTART.md                # Quick start guide
│                                # - Simplified startup steps
│                                # - Common issues
│
└── PROJECT_OVERVIEW.md          # Project overview
                                 # - Architecture design
                                 # - Technical details
                                 # - Expansion directions
```
