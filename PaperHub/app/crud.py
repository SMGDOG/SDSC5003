"""
CRUD (Create, Read, Update, Delete) operations for database models
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc, func
from typing import List, Optional
from datetime import datetime
import numpy as np

from app.models import Paper, Tag, PaperTag, ReadingHistory
from app.schemas import PaperCreate, PaperUpdate, TagCreate, ReadingHistoryCreate


# ==================== Paper CRUD ====================

def create_paper(db: Session, paper: PaperCreate, embedding: Optional[List[float]] = None) -> Paper:
    """创建论文"""
    db_paper = Paper(
        title=paper.title,
        authors=paper.authors,
        abstract=paper.abstract,
        pdf_url=paper.pdf_url,
        arxiv_id=paper.arxiv_id,
        category=paper.category,
        published_date=paper.published_date,
        embedding=embedding
    )
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    
    # 添加标签关联
    if paper.tag_ids:
        for tag_id in paper.tag_ids:
            paper_tag = PaperTag(paper_id=db_paper.id, tag_id=tag_id)
            db.add(paper_tag)
        db.commit()
        db.refresh(db_paper)
    
    return db_paper


def get_paper(db: Session, paper_id: int) -> Optional[Paper]:
    """获取单个论文"""
    return db.query(Paper).options(
        joinedload(Paper.paper_tags).joinedload(PaperTag.tag)
    ).filter(Paper.id == paper_id).first()


def get_paper_by_arxiv_id(db: Session, arxiv_id: str) -> Optional[Paper]:
    """通过 arXiv ID 获取论文"""
    return db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()


def get_papers(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    query: Optional[str] = None,
    category: Optional[str] = None,
    tag_ids: Optional[List[int]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Paper]:
    """获取论文列表（支持多条件筛选）"""
    db_query = db.query(Paper).options(
        joinedload(Paper.paper_tags).joinedload(PaperTag.tag)
    )
    
    # 文本搜索（标题或摘要）
    if query:
        search_filter = or_(
            Paper.title.ilike(f"%{query}%"),
            Paper.abstract.ilike(f"%{query}%")
        )
        db_query = db_query.filter(search_filter)
    
    # 类别筛选
    if category:
        db_query = db_query.filter(Paper.category == category)
    
    # 标签筛选
    if tag_ids:
        db_query = db_query.join(PaperTag).filter(PaperTag.tag_id.in_(tag_ids))
    
    # 日期范围筛选
    if start_date:
        db_query = db_query.filter(Paper.published_date >= start_date)
    if end_date:
        db_query = db_query.filter(Paper.published_date <= end_date)
    
    return db_query.order_by(desc(Paper.published_date)).offset(skip).limit(limit).all()


def update_paper(db: Session, paper_id: int, paper_update: PaperUpdate) -> Optional[Paper]:
    """更新论文"""
    db_paper = get_paper(db, paper_id)
    if not db_paper:
        return None
    
    update_data = paper_update.model_dump(exclude_unset=True, exclude={'tag_ids'})
    for field, value in update_data.items():
        setattr(db_paper, field, value)
    
    # 更新标签关联
    if paper_update.tag_ids is not None:
        # 删除旧关联
        db.query(PaperTag).filter(PaperTag.paper_id == paper_id).delete()
        # 添加新关联
        for tag_id in paper_update.tag_ids:
            paper_tag = PaperTag(paper_id=paper_id, tag_id=tag_id)
            db.add(paper_tag)
    
    db.commit()
    db.refresh(db_paper)
    return db_paper


def delete_paper(db: Session, paper_id: int) -> bool:
    """删除论文"""
    db_paper = get_paper(db, paper_id)
    if not db_paper:
        return False
    
    db.delete(db_paper)
    db.commit()
    return True


def update_paper_embedding(db: Session, paper_id: int, embedding: List[float]) -> Optional[Paper]:
    """更新论文的 embedding"""
    db_paper = get_paper(db, paper_id)
    if not db_paper:
        return None
    
    db_paper.embedding = embedding
    db.commit()
    db.refresh(db_paper)
    return db_paper


# ==================== Tag CRUD ====================

def create_tag(db: Session, tag: TagCreate) -> Tag:
    """创建标签"""
    db_tag = Tag(name=tag.name, description=tag.description)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
    """获取单个标签"""
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_tag_by_name(db: Session, name: str) -> Optional[Tag]:
    """通过名称获取标签"""
    return db.query(Tag).filter(Tag.name == name).first()


def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[Tag]:
    """获取标签列表"""
    return db.query(Tag).order_by(Tag.name).offset(skip).limit(limit).all()


def get_or_create_tag(db: Session, name: str, description: Optional[str] = None) -> Tag:
    """获取或创建标签"""
    tag = get_tag_by_name(db, name)
    if not tag:
        tag = create_tag(db, TagCreate(name=name, description=description))
    return tag


def delete_tag(db: Session, tag_id: int) -> bool:
    """删除标签"""
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return False
    
    db.delete(db_tag)
    db.commit()
    return True


# ==================== ReadingHistory CRUD ====================

def create_reading_history(db: Session, history: ReadingHistoryCreate) -> ReadingHistory:
    """创建阅读历史"""
    db_history = ReadingHistory(
        paper_id=history.paper_id,
        user_id=history.user_id,
        rating=history.rating,
        notes=history.notes
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history


def get_reading_history(db: Session, history_id: int) -> Optional[ReadingHistory]:
    """获取单条阅读历史"""
    return db.query(ReadingHistory).options(
        joinedload(ReadingHistory.paper)
    ).filter(ReadingHistory.id == history_id).first()


def get_reading_histories(
    db: Session,
    user_id: str = "default_user",
    skip: int = 0,
    limit: int = 50
) -> List[ReadingHistory]:
    """获取用户阅读历史列表"""
    return db.query(ReadingHistory).options(
        joinedload(ReadingHistory.paper)
    ).filter(
        ReadingHistory.user_id == user_id
    ).order_by(
        desc(ReadingHistory.read_at)
    ).offset(skip).limit(limit).all()


def get_user_read_paper_ids(db: Session, user_id: str = "default_user") -> List[int]:
    """获取用户已读论文 ID 列表"""
    results = db.query(ReadingHistory.paper_id).filter(
        ReadingHistory.user_id == user_id
    ).distinct().all()
    return [r[0] for r in results]


def delete_reading_history(db: Session, history_id: int) -> bool:
    """删除阅读历史"""
    db_history = get_reading_history(db, history_id)
    if not db_history:
        return False
    
    db.delete(db_history)
    db.commit()
    return True


# ==================== 统计函数 ====================

def get_paper_count(db: Session) -> int:
    """获取论文总数"""
    return db.query(func.count(Paper.id)).scalar()


def get_tag_count(db: Session) -> int:
    """获取标签总数"""
    return db.query(func.count(Tag.id)).scalar()


def get_categories(db: Session) -> List[str]:
    """获取所有论文类别"""
    results = db.query(Paper.category).filter(
        Paper.category.isnot(None)
    ).distinct().all()
    return sorted([r[0] for r in results if r[0]])
