"""
Qwen3-Reranker Cross-Encoder 集成模块

本模块实现了Qwen3-Reranker cross-encoder模型，用于对初步检索结果进行高质量重排序。
Cross-encoder模型通过直接对"查询-文档"对进行打分，比双塔模型具有更高的相关性判断精度。

主要功能：
1. 加载Qwen3-Reranker模型（支持本地量化模型）
2. 对查询和候选文档进行相关性打分
3. 返回yes/no概率作为相关性分数

使用示例：
    reranker = Qwen3Reranker()
    scores = reranker.rerank("查询文本", ["文档1", "文档2", "文档3"])
    # scores: [0.92, 0.45, 0.78] - 分数越高表示相关性越强
"""
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class Qwen3Reranker:
    """
    Qwen3-Reranker Cross-Encoder 重排序器
    
    使用Qwen3-Reranker模型对查询和候选文档进行相关性打分。
    支持本地量化模型，显存占用低，推理速度快。
    """
    
    def __init__(self, model_name="Qwen3-Reranker-4B:Q4_K_M", device=None):
        """
        初始化Qwen3-Reranker模型
        
        Args:
            model_name (str): 模型名称，默认使用量化版本
            device (str): 设备类型，None表示自动选择
        """
        print(f"正在加载Qwen3-Reranker模型: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto" if device is None else device,
            torch_dtype=torch.float16,
            attn_implementation="flash_attention_2"
        )
        
        # 获取yes/no token的ID
        self.yes_token_id = self.tokenizer.encode("yes")[0]
        self.no_token_id = self.tokenizer.encode("no")[0]
        print("Qwen3-Reranker模型加载完成")

    def build_input(self, query, chunk):
        """
        构建模型输入格式
        
        Args:
            query (str): 用户查询
            chunk (str): 候选文档片段
            
        Returns:
            str: 格式化的输入文本
        """
        system_prompt = "<|im_start|>system 请判断以下文档是否满足检索要求。<|im_end|>"
        instruction = "判断文档与查询的语义相关性"
        return f"{system_prompt}<|im_start|>user 指令：{instruction} 查询：{query} 文档：{chunk}<|im_end|>"

    def rerank(self, query, chunks):
        """
        对候选文档进行重排序打分
        
        Args:
            query (str): 用户查询
            chunks (list): 候选文档列表
            
        Returns:
            list: 相关性分数列表，分数越高表示相关性越强
        """
        # 构建所有输入
        inputs = [self.build_input(query, chunk) for chunk in chunks]
        
        # 批量编码
        encodings = self.tokenizer(
            inputs, 
            return_tensors="pt", 
            padding=True, 
            truncation=True, 
            max_length=512
        ).to(self.model.device)
        
        # 推理
        with torch.no_grad():
            outputs = self.model(**encodings)
            logits = outputs.logits[:, -1, :]  # 取每个输入最后一个token的logits
        
        # 计算yes/no概率
        yes_logits = logits[:, self.yes_token_id]
        no_logits = logits[:, self.no_token_id]
        scores = torch.softmax(torch.stack([yes_logits, no_logits], dim=1), dim=1)[:, 0]  # yes的概率
        
        return scores.tolist() 