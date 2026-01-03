# agent/llm_aliyun.py
import os
from langchain.llms.base import LLM
from typing import Optional, List
import dashscope

class AliyunQwenLLM(LLM):
    """阿里云百炼 Qwen LLM 封装"""

    model_name: str = "qwen-turbo"
    temperature: float = 0.2

    @property
    def _llm_type(self) -> str:
        return "aliyun_qwen"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
    ) -> str:
        response = dashscope.Generation.call(
            model=self.model_name,
            prompt=prompt,
            temperature=self.temperature,
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            result_format="text",
        )

        if response.status_code != 200:
            raise RuntimeError(f"DashScope error: {response}")

        return response.output.text
