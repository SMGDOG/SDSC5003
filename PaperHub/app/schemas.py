"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class TagBase(BaseModel):
    """标签基础模型"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class TagCreate(TagBase):
    """创建标签"""
    pass


class TagResponse(TagBase):
    """标签响应"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PaperBase(BaseModel):
    """论文基础模型"""
    title: str = Field(..., min_length=1, max_length=500)
    authors: List[str] = Field(..., min_items=1)
    abstract: Optional[str] = None
    pdf_url: Optional[str] = None
    arxiv_id: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    published_date: Optional[datetime] = None


class PaperCreate(PaperBase):
    """创建论文"""
    tag_ids: Optional[List[int]] = []


class PaperUpdate(BaseModel):
    """更新论文"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    authors: Optional[List[str]] = None
    abstract: Optional[str] = None
    pdf_url: Optional[str] = None
    category: Optional[str] = None
    published_date: Optional[datetime] = None
    tag_ids: Optional[List[int]] = None


class PaperResponse(PaperBase):
    """论文响应"""
    id: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True


class PaperWithSimilarity(PaperResponse):
    """带相似度的论文"""
    similarity_score: Optional[float] = None


class ReadingHistoryBase(BaseModel):
    """阅读历史基础模型"""
    paper_id: int
    user_id: str = "default_user"
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class ReadingHistoryCreate(ReadingHistoryBase):
    """创建阅读历史"""
    pass


class ReadingHistoryResponse(ReadingHistoryBase):
    """阅读历史响应"""
    id: int
    read_at: datetime
    paper: Optional[PaperResponse] = None

    class Config:
        from_attributes = True


class PaperSearchRequest(BaseModel):
    """论文搜索请求"""
    query: Optional[str] = None
    category: Optional[str] = None
    tag_ids: Optional[List[int]] = []
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)


class ArxivImportRequest(BaseModel):
    """arXiv 导入请求"""
    query: str = Field(..., min_length=1)
    max_results: int = Field(10, ge=1, le=100)
    category: Optional[str] = None
    auto_tag: bool = True  # 自动根据类别创建标签
