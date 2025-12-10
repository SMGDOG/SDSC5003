"""
工具函数：arXiv 爬虫、文本处理等
"""
import arxiv
from typing import List, Dict, Optional
from datetime import datetime
import time
import re


def clean_text(text: str) -> str:
    """
    清理文本：移除多余空白、换行符等
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    
    # 替换多个空白字符为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 去除首尾空白
    text = text.strip()
    return text


def extract_arxiv_id(url_or_id: str) -> Optional[str]:
    """
    从 URL 或字符串中提取 arXiv ID
    
    Args:
        url_or_id: arXiv URL 或 ID
        
    Returns:
        arXiv ID 或 None
    
    Examples:
        'https://arxiv.org/abs/2301.12345' -> '2301.12345'
        'arxiv:2301.12345' -> '2301.12345'
        '2301.12345' -> '2301.12345'
    """
    if not url_or_id:
        return None
    
    # 匹配 arXiv ID 格式 (YYMM.NNNNN 或 arch-ive/YYMMNNN)
    patterns = [
        r'arxiv\.org/abs/(\d{4}\.\d{4,5})',
        r'arxiv:(\d{4}\.\d{4,5})',
        r'^(\d{4}\.\d{4,5})$',
        r'arxiv\.org/abs/([a-z\-]+/\d{7})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def search_arxiv_papers(
    query: str,
    max_results: int = 10,
    sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance,
    sort_order: arxiv.SortOrder = arxiv.SortOrder.Descending
) -> List[Dict]:
    """
    搜索 arXiv 论文
    
    Args:
        query: 搜索查询字符串
        max_results: 最大结果数
        sort_by: 排序标准
        sort_order: 排序顺序
        
    Returns:
        论文信息字典列表
    """
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    papers = []
    for result in search.results():
        paper = {
            'title': clean_text(result.title),
            'authors': [author.name for author in result.authors],
            'abstract': clean_text(result.summary),
            'pdf_url': result.pdf_url,
            'arxiv_id': result.entry_id.split('/abs/')[-1],
            'category': result.primary_category,
            'published_date': result.published,
            'updated_date': result.updated,
            'categories': result.categories,
            'comment': result.comment,
            'journal_ref': result.journal_ref,
        }
        papers.append(paper)
        time.sleep(0.5)  # 避免请求过快
    
    return papers


def fetch_arxiv_by_id(arxiv_id: str) -> Optional[Dict]:
    """
    通过 arXiv ID 获取论文详情
    
    Args:
        arxiv_id: arXiv ID
        
    Returns:
        论文信息字典或 None
    """
    search = arxiv.Search(id_list=[arxiv_id])
    
    try:
        result = next(search.results())
        paper = {
            'title': clean_text(result.title),
            'authors': [author.name for author in result.authors],
            'abstract': clean_text(result.summary),
            'pdf_url': result.pdf_url,
            'arxiv_id': result.entry_id.split('/abs/')[-1],
            'category': result.primary_category,
            'published_date': result.published,
            'updated_date': result.updated,
            'categories': result.categories,
        }
        return paper
    except StopIteration:
        return None


def search_arxiv_by_category(
    category: str,
    max_results: int = 50,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict]:
    """
    按类别搜索 arXiv 论文
    
    Args:
        category: arXiv 分类 (如 cs.AI, cs.LG, math.CO)
        max_results: 最大结果数
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        论文信息字典列表
    """
    query = f"cat:{category}"
    
    # 添加日期范围（如果指定）
    if start_date or end_date:
        date_query_parts = []
        if start_date:
            date_query_parts.append(f"submittedDate:[{start_date.strftime('%Y%m%d')}* TO *]")
        if end_date:
            date_query_parts.append(f"submittedDate:[* TO {end_date.strftime('%Y%m%d')}*]")
        if date_query_parts:
            query += " AND " + " AND ".join(date_query_parts)
    
    return search_arxiv_papers(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )


def format_authors(authors: List[str], max_display: int = 3) -> str:
    """
    格式化作者列表为显示字符串
    
    Args:
        authors: 作者列表
        max_display: 最多显示的作者数
        
    Returns:
        格式化的作者字符串
    
    Examples:
        ['A', 'B', 'C', 'D'] -> 'A, B, C, et al.'
    """
    if not authors:
        return "Unknown"
    
    if len(authors) <= max_display:
        return ", ".join(authors)
    else:
        displayed = ", ".join(authors[:max_display])
        return f"{displayed}, et al."


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        截断后的文本
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def get_arxiv_categories() -> Dict[str, str]:
    """
    获取常见的 arXiv 分类及其描述
    
    Returns:
        {category_code: description} 字典
    """
    return {
        # Computer Science
        'cs.AI': 'Artificial Intelligence',
        'cs.CL': 'Computation and Language',
        'cs.CV': 'Computer Vision and Pattern Recognition',
        'cs.LG': 'Machine Learning',
        'cs.NE': 'Neural and Evolutionary Computing',
        'cs.RO': 'Robotics',
        'cs.CR': 'Cryptography and Security',
        'cs.DB': 'Databases',
        'cs.DS': 'Data Structures and Algorithms',
        'cs.IR': 'Information Retrieval',
        
        # Mathematics
        'math.CO': 'Combinatorics',
        'math.ST': 'Statistics Theory',
        'math.OC': 'Optimization and Control',
        'math.PR': 'Probability',
        
        # Physics
        'physics.comp-ph': 'Computational Physics',
        'physics.data-an': 'Data Analysis, Statistics and Probability',
        
        # Statistics
        'stat.ML': 'Machine Learning (Statistics)',
        'stat.AP': 'Applications',
        'stat.CO': 'Computation',
        
        # Quantitative Biology
        'q-bio.QM': 'Quantitative Methods',
        'q-bio.GN': 'Genomics',
    }


def validate_arxiv_id(arxiv_id: str) -> bool:
    """
    验证 arXiv ID 格式是否正确
    
    Args:
        arxiv_id: arXiv ID
        
    Returns:
        是否有效
    """
    if not arxiv_id:
        return False
    
    # 新格式: YYMM.NNNNN
    if re.match(r'^\d{4}\.\d{4,5}$', arxiv_id):
        return True
    
    # 旧格式: arch-ive/YYMMNNN
    if re.match(r'^[a-z\-]+/\d{7}$', arxiv_id):
        return True
    
    return False
