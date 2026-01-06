import json
import os
from typing import Any, Dict, Iterator

from openai import OpenAI


def build_payload(composition_frac: Dict[str, float], process: Dict[str, Any], target: str) -> Dict[str, Any]:
    return {"composition": composition_frac, "process": process, "target_property": target}

def call_llm(
    model_name: str,
    prompts: Dict[str, str],
    payload: Dict[str, Any],
    deep_think: bool = True,
) -> Iterator[str]:
    """
    Stream tokens (yield str chunks) for Streamlit write_stream().
    """
    if model_name == "DeepSeek-R1-0628":
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set in environment variables.")

        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )

        model = "deepseek-reasoner" if deep_think else "deepseek-chat"

        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompts["query_with_know"]},
            ],
            stream=True,
        )

        for event in stream:
            # OpenAI-compatible streaming: delta may contain content chunks
            delta = event.choices[0].delta
            # 1️⃣ DeepThink 推理内容（<think>）
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                yield ("think", delta.reasoning_content)

            # 2️⃣ 最终回答内容
            elif hasattr(delta, "content") and delta.content:
                yield ("final", delta.content)
        return

    raise NotImplementedError("LLM call not implemented yet.")
