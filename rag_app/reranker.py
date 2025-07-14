"""
Qwen3-Reranker集成模块
"""
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class Qwen3Reranker:
    def __init__(self, model_name="Qwen3-Reranker-4B:Q4_K_M", device=None):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto" if device is None else device,
            torch_dtype=torch.float16,
            attn_implementation="flash_attention_2"
        )
        self.yes_token_id = self.tokenizer.encode("yes")[0]
        self.no_token_id = self.tokenizer.encode("no")[0]

    def build_input(self, query, chunk):
        system_prompt = "<|im_start|>system 请判断以下文档是否满足检索要求。<|im_end|>"
        instruction = "判断文档与查询的语义相关性"
        return f"{system_prompt}<|im_start|>user 指令：{instruction} 查询：{query} 文档：{chunk}<|im_end|>"

    def rerank(self, query, chunks):
        # 支持批量
        inputs = [self.build_input(query, chunk) for chunk in chunks]
        encodings = self.tokenizer(
            inputs, return_tensors="pt", padding=True, truncation=True, max_length=512
        ).to(self.model.device)
        with torch.no_grad():
            outputs = self.model(**encodings)
            logits = outputs.logits[:, -1, :]  # 取每个输入最后一个token的logits
        yes_logits = logits[:, self.yes_token_id]
        no_logits = logits[:, self.no_token_id]
        scores = torch.softmax(torch.stack([yes_logits, no_logits], dim=1), dim=1)[:, 0]  # yes的概率
        return scores.tolist() 