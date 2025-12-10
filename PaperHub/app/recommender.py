"""
智能推荐引擎
基于 sentence-transformers 的语义相似度推荐
"""
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np
import os

from app.models import Paper
from app.crud import get_user_read_paper_ids


class PaperRecommender:
    """论文推荐引擎"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        初始化推荐引擎
        
        Args:
            model_name: sentence-transformers 模型名称
        """
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # all-MiniLM-L6-v2 的向量维度
    
    def load_model(self):
        """延迟加载模型（避免启动时占用过多资源）"""
        if self.model is None:
            print(f"正在加载模型: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            print("模型加载完成！")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本的 embedding
        
        Args:
            text: 输入文本
            
        Returns:
            embedding 向量
        """
        self.load_model()
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_paper_embedding(self, paper: Paper) -> List[float]:
        """
        生成论文的 embedding（基于标题和摘要）
        
        Args:
            paper: 论文对象
            
        Returns:
            embedding 向量
        """
        # 组合标题和摘要
        text_parts = [paper.title]
        if paper.abstract:
            text_parts.append(paper.abstract[:500])  # 限制摘要长度
        
        combined_text = " ".join(text_parts)
        return self.generate_embedding(combined_text)
    
    def find_similar_papers(
        self,
        db: Session,
        query_embedding: List[float],
        limit: int = 10,
        exclude_ids: Optional[List[int]] = None
    ) -> List[Tuple[Paper, float]]:
        """
        使用向量相似度搜索相似论文
        
        Args:
            db: 数据库会话
            query_embedding: 查询向量
            limit: 返回数量
            exclude_ids: 要排除的论文 ID 列表
            
        Returns:
            (论文, 相似度分数) 元组列表
        """
        # 构建 SQL 查询（使用余弦相似度）
        exclude_clause = ""
        if exclude_ids:
            exclude_ids_str = ",".join(map(str, exclude_ids))
            exclude_clause = f"AND id NOT IN ({exclude_ids_str})"
        
        # 将 Python 列表转换为 pgvector 兼容的字符串格式
        # 确保使用标准小数格式，避免科学计数法
        vector_str = '[' + ','.join([f'{float(x):.10f}' for x in query_embedding]) + ']'
        
        # pgvector 使用 <=> 操作符计算余弦距离（距离越小，相似度越高）
        # 1 - distance 得到相似度分数
        # 直接将向量嵌入 SQL 中，避免参数绑定问题
        query = text(f"""
            SELECT 
                id,
                title,
                authors,
                abstract,
                pdf_url,
                arxiv_id,
                category,
                published_date,
                created_at,
                updated_at,
                1 - (embedding <=> '{vector_str}'::vector) as similarity
            FROM papers
            WHERE embedding IS NOT NULL
            {exclude_clause}
            ORDER BY embedding <=> '{vector_str}'::vector
            LIMIT :limit
        """)
        
        result = db.execute(
            query,
            {"limit": limit}
        )
        
        papers_with_scores = []
        for row in result:
            paper = Paper(
                id=row.id,
                title=row.title,
                authors=row.authors,
                abstract=row.abstract,
                pdf_url=row.pdf_url,
                arxiv_id=row.arxiv_id,
                category=row.category,
                published_date=row.published_date,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            papers_with_scores.append((paper, float(row.similarity)))
        
        return papers_with_scores
    
    def recommend_by_paper(
        self,
        db: Session,
        paper_id: int,
        limit: int = 10,
        exclude_current: bool = True
    ) -> List[Tuple[Paper, float]]:
        """
        基于单篇论文推荐相似论文
        
        Args:
            db: 数据库会话
            paper_id: 论文 ID
            limit: 返回数量
            exclude_current: 是否排除当前论文
            
        Returns:
            (论文, 相似度分数) 元组列表
        """
        # 获取目标论文
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper or paper.embedding is None:
            return []
        
        exclude_ids = [paper_id] if exclude_current else []
        return self.find_similar_papers(db, paper.embedding, limit, exclude_ids)
    
    def recommend_by_reading_history(
        self,
        db: Session,
        user_id: str = "default_user",
        limit: int = 10,
        history_limit: int = 10
    ) -> List[Tuple[Paper, float]]:
        """
        基于用户阅读历史推荐论文（个性化推荐）
        
        策略：
        1. 获取用户最近阅读的论文
        2. 计算这些论文 embedding 的平均值
        3. 找到与平均 embedding 最相似的论文
        
        Args:
            db: 数据库会话
            user_id: 用户 ID
            limit: 返回数量
            history_limit: 考虑的历史记录数量
            
        Returns:
            (论文, 相似度分数) 元组列表
        """
        # 获取用户已读论文 ID
        read_paper_ids = get_user_read_paper_ids(db, user_id)
        if not read_paper_ids:
            return []
        
        # 获取最近阅读的论文（有 embedding 的）
        recent_papers = db.query(Paper).filter(
            Paper.id.in_(read_paper_ids[:history_limit]),
            Paper.embedding.isnot(None)
        ).all()
        
        if not recent_papers:
            return []
        
        # 计算平均 embedding
        embeddings = np.array([p.embedding for p in recent_papers])
        avg_embedding = np.mean(embeddings, axis=0).tolist()
        
        # 查找相似论文（排除已读）
        return self.find_similar_papers(db, avg_embedding, limit, read_paper_ids)
    
    def recommend_hybrid(
        self,
        db: Session,
        paper_id: int,
        user_id: str = "default_user",
        limit: int = 10
    ) -> List[Tuple[Paper, float]]:
        """
        混合推荐：结合当前论文和用户历史
        
        Args:
            db: 数据库会话
            paper_id: 当前论文 ID
            user_id: 用户 ID
            limit: 返回数量
            
        Returns:
            (论文, 相似度分数) 元组列表
        """
        # 获取当前论文
        current_paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not current_paper or current_paper.embedding is None:
            return []
        
        # 获取用户已读论文
        read_paper_ids = get_user_read_paper_ids(db, user_id)
        recent_papers = db.query(Paper).filter(
            Paper.id.in_(read_paper_ids[:5]),
            Paper.embedding.isnot(None)
        ).all() if read_paper_ids else []
        
        # 混合策略：70% 当前论文，30% 用户历史
        if recent_papers:
            current_embedding = np.array(current_paper.embedding)
            history_embeddings = np.array([p.embedding for p in recent_papers])
            avg_history_embedding = np.mean(history_embeddings, axis=0)
            
            hybrid_embedding = (0.7 * current_embedding + 0.3 * avg_history_embedding).tolist()
        else:
            hybrid_embedding = current_paper.embedding
        
        # 排除当前论文和已读论文
        exclude_ids = [paper_id] + read_paper_ids
        return self.find_similar_papers(db, hybrid_embedding, limit, exclude_ids)


# 全局单例
recommender = PaperRecommender()
