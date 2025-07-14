#!/usr/bin/env python3
"""
测试新功能的脚本
测试监视模块和Qwen3-Reranker精排功能
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8000"

def test_monitor_stats():
    """测试监视统计API"""
    print("\n=== 测试监视统计API ===")
    try:
        response = requests.get(f"{BASE_URL}/monitor/stats")
        if response.status_code == 200:
            data = response.json()
            print("✅ 监视统计API测试成功")
            print(f"集合名称: {data.get('collection_name', 'N/A')}")
            print(f"总文档数: {data.get('total_documents', 'N/A')}")
            if 'content_analysis' in data:
                content_analysis = data['content_analysis']
                print(f"平均长度: {content_analysis.get('avg_length', 'N/A')}")
        else:
            print(f"❌ 监视统计API测试失败: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ 监视统计API测试异常: {e}")

def test_monitor_samples():
    """测试监视样本API"""
    print("\n=== 测试监视样本API ===")
    try:
        response = requests.get(f"{BASE_URL}/monitor/samples?limit=5")
        if response.status_code == 200:
            data = response.json()
            print("✅ 监视样本API测试成功")
            print(f"样本数量: {len(data.get('samples', []))}")
            print(f"总文档数: {data.get('pagination', {}).get('total', 'N/A')}")
        else:
            print(f"❌ 监视样本API测试失败: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ 监视样本API测试异常: {e}")

def test_reranked_search():
    """测试Qwen3-Reranker精排搜索"""
    print("\n=== 测试Qwen3-Reranker精排搜索API ===")
    try:
        payload = {
            "query": "python里怎么定义一个函数",
            "top_k": 3
        }
        response = requests.post(
            f"{BASE_URL}/search/reranked",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Qwen3-Reranker精排搜索API测试成功")
            print(f"查询: {data.get('query', 'N/A')}")
            print(f"精排策略: {data.get('rerank_strategy', 'N/A')}")
            print(f"结果数量: {len(data.get('results', []))}")
            
            # 显示前3个结果
            for i, result in enumerate(data.get('results', [])[:3]):
                print(f"  结果 {i+1}:")
                print(f"    ID: {result.get('id', 'N/A')}")
                print(f"    内容: {result.get('content', 'N/A')[:50]}...")
                print(f"    精排分数: {result.get('rerank_score', 'N/A')}")
                print(f"    最终排名: {result.get('final_rank', 'N/A')}")
        else:
            print(f"❌ Qwen3-Reranker精排搜索API测试失败: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Qwen3-Reranker精排搜索API测试异常: {e}")

def test_regular_search():
    """测试普通搜索作为对比"""
    print("\n=== 测试普通搜索API ===")
    try:
        payload = {
            "query": "python里怎么定义一个函数",
            "top_k": 3
        }
        response = requests.post(
            f"{BASE_URL}/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ 普通搜索API测试成功")
            print(f"查询: {data.get('query', 'N/A')}")
            print(f"结果数量: {len(data.get('results', []))}")
        else:
            print(f"❌ 普通搜索API测试失败: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ 普通搜索API测试异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试RAGdemo新功能...")
    print(f"API服务地址: {BASE_URL}")
    
    # 等待服务启动
    print("等待API服务启动...")
    time.sleep(2)
    
    # 测试各个功能
    test_monitor_stats()
    test_monitor_samples()
    test_regular_search()
    test_reranked_search()
    
    print("\n🎉 测试完成！")
    print("💡 提示: 访问 http://localhost:8000/monitor 查看监视页面")

if __name__ == "__main__":
    main() 