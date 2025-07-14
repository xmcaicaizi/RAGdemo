"""
监视模块 - 提供知识库监控和数据可视化功能
该模块实现了KnowledgeBaseMonitor类，用于查看RAG库中的数据片段和统计信息
"""

import chromadb
import pandas as pd
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

from . import config

class KnowledgeBaseMonitor:
    """
    知识库监视器类
    提供查看RAG库数据片段、统计信息和可视化功能
    """
    
    def __init__(self):
        """
        初始化知识库监视器
        """
        print("正在初始化知识库监视器...")
        self.config = config
        self.client = chromadb.PersistentClient(path=self.config.CHROMA_PATH)
        print(f"知识库监视器已连接到: {self.config.CHROMA_PATH}")
    
    def get_collections_info(self) -> Dict[str, Any]:
        """
        获取所有集合的基本信息
        
        返回:
            Dict: 包含集合信息的字典
        """
        try:
            collections = self.client.list_collections()
            collections_info = []
            
            for collection in collections:
                collection_info = {
                    "name": collection.name,
                    "count": collection.count(),
                    "metadata": collection.metadata or {}
                }
                collections_info.append(collection_info)
            
            return {
                "total_collections": len(collections_info),
                "collections": collections_info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"获取集合信息失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_collection_stats(self, collection_name: str = None) -> Dict[str, Any]:
        """
        获取指定集合的详细统计信息
        
        参数:
            collection_name (str): 集合名称，如果为None则使用默认集合
            
        返回:
            Dict: 包含统计信息的字典
        """
        try:
            if collection_name is None:
                collection_name = self.config.COLLECTION_NAME
            
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            
            # 获取所有数据用于分析
            all_data = collection.get()
            
            # 分析元数据
            metadata_analysis = self._analyze_metadata(all_data.get('metadatas', []))
            
            # 分析内容长度
            content_lengths = [len(doc) for doc in all_data.get('documents', [])]
            
            stats = {
                "collection_name": collection_name,
                "total_documents": count,
                "metadata_analysis": metadata_analysis,
                "content_analysis": {
                    "avg_length": sum(content_lengths) / len(content_lengths) if content_lengths else 0,
                    "min_length": min(content_lengths) if content_lengths else 0,
                    "max_length": max(content_lengths) if content_lengths else 0,
                    "length_distribution": self._get_length_distribution(content_lengths)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return stats
        except Exception as e:
            return {
                "error": f"获取集合统计信息失败: {str(e)}",
                "collection_name": collection_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_data_samples(self, collection_name: str = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        获取数据样本
        
        参数:
            collection_name (str): 集合名称
            limit (int): 返回的样本数量
            offset (int): 偏移量
            
        返回:
            Dict: 包含数据样本的字典
        """
        try:
            if collection_name is None:
                collection_name = self.config.COLLECTION_NAME
            
            collection = self.client.get_collection(name=collection_name)
            
            # 获取所有数据
            all_data = collection.get()
            
            # 计算实际的范围
            total_count = len(all_data.get('ids', []))
            start_idx = min(offset, total_count)
            end_idx = min(start_idx + limit, total_count)
            
            samples = []
            for i in range(start_idx, end_idx):
                sample = {
                    "id": all_data['ids'][i],
                    "content": all_data['documents'][i],
                    "metadata": all_data['metadatas'][i],
                    "index": i
                }
                samples.append(sample)
            
            return {
                "collection_name": collection_name,
                "samples": samples,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": end_idx < total_count
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"获取数据样本失败: {str(e)}",
                "collection_name": collection_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def search_and_monitor(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        执行搜索并返回详细的监控信息
        
        参数:
            query (str): 搜索查询
            top_k (int): 返回结果数量
            
        返回:
            Dict: 包含搜索结果和监控信息的字典
        """
        try:
            collection = self.client.get_collection(name=self.config.COLLECTION_NAME)
            results = collection.query(query_texts=[query], n_results=top_k)
            
            search_results = []
            if results and results.get('ids') and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i],
                        "rank": i + 1
                    }
                    search_results.append(result)
            
            return {
                "query": query,
                "results": search_results,
                "total_found": len(search_results),
                "search_metadata": {
                    "top_k": top_k,
                    "collection_name": self.config.COLLECTION_NAME,
                    "embedding_provider": self.config.EMBEDDING_PROVIDER
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"搜索监控失败: {str(e)}",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_metadata(self, metadatas: List[Dict]) -> Dict[str, Any]:
        """
        分析元数据
        
        参数:
            metadatas (List[Dict]): 元数据列表
            
        返回:
            Dict: 元数据分析结果
        """
        if not metadatas:
            return {"error": "没有元数据"}
        
        # 统计字段出现频率
        field_counts = {}
        for metadata in metadatas:
            for key, value in metadata.items():
                if key not in field_counts:
                    field_counts[key] = {}
                if value not in field_counts[key]:
                    field_counts[key][value] = 0
                field_counts[key][value] += 1
        
        # 计算字段统计信息
        field_stats = {}
        for field, values in field_counts.items():
            field_stats[field] = {
                "unique_values": len(values),
                "total_occurrences": sum(values.values()),
                "most_common": max(values.items(), key=lambda x: x[1]) if values else None,
                "value_distribution": values
            }
        
        return {
            "total_metadata_entries": len(metadatas),
            "field_statistics": field_stats,
            "available_fields": list(field_counts.keys())
        }
    
    def _get_length_distribution(self, lengths: List[int]) -> Dict[str, int]:
        """
        获取内容长度分布
        
        参数:
            lengths (List[int]): 长度列表
            
        返回:
            Dict: 长度分布
        """
        if not lengths:
            return {}
        
        distribution = {
            "short (0-50)": 0,
            "medium (51-200)": 0,
            "long (201-500)": 0,
            "very_long (500+)": 0
        }
        
        for length in lengths:
            if length <= 50:
                distribution["short (0-50)"] += 1
            elif length <= 200:
                distribution["medium (51-200)"] += 1
            elif length <= 500:
                distribution["long (201-500)"] += 1
            else:
                distribution["very_long (500+)"] += 1
        
        return distribution 