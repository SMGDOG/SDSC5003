"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector as VECTOR
from app.database import Base
import datetime


class Paper(Base):
    """论文模型"""
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    authors = Column(JSON, nullable=False)  # 存储作者列表 ["Author1", "Author2"]
    abstract = Column(Text, nullable=True)
    pdf_url = Column(String(500), nullable=True)
    arxiv_id = Column(String(50), unique=True, nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    published_date = Column(DateTime, nullable=True, index=True)
    embedding = Column(VECTOR(384), nullable=True)  # 使用 all-MiniLM-L6-v2 生成的向量
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # 关系
    paper_tags = relationship("PaperTag", back_populates="paper", cascade="all, delete-orphan")
    reading_histories = relationship("ReadingHistory", back_populates="paper", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Paper(id={self.id}, title={self.title[:50]}...)>"


class Tag(Base):
    """标签模型"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # 关系
    paper_tags = relationship("PaperTag", back_populates="tag", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class PaperTag(Base):
    """论文-标签关联表（多对多）"""
    __tablename__ = "paper_tags"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # 关系
    paper = relationship("Paper", back_populates="paper_tags")
    tag = relationship("Tag", back_populates="paper_tags")

    # 唯一约束
    __table_args__ = (
        Index('ix_paper_tag_unique', 'paper_id', 'tag_id', unique=True),
    )

    def __repr__(self):
        return f"<PaperTag(paper_id={self.paper_id}, tag_id={self.tag_id})>"


class ReadingHistory(Base):
    """阅读历史记录"""
    __tablename__ = "reading_histories"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(100), default="default_user", nullable=False, index=True)  # 支持多用户扩展
    read_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    rating = Column(Integer, nullable=True)  # 评分 1-5
    notes = Column(Text, nullable=True)  # 用户笔记

    # 关系
    paper = relationship("Paper", back_populates="reading_histories")

    def __repr__(self):
        return f"<ReadingHistory(id={self.id}, paper_id={self.paper_id}, user_id={self.user_id})>"
