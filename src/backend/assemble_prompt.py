from prompt import *
from config import EvalCalculateColumns, CalculateColumnsDesc
from typing import Dict, Any, List
import pandas as pd


def assemble_calculate_desc(target_name, cal_dict):
    calculate_columns = EvalCalculateColumns[target_name]
    desc_parts = []
    for col in calculate_columns:
        if col in cal_dict and pd.notna(cal_dict[col]):
            desc_parts.append(CalculateColumnsDesc[col].format(value=cal_dict[col]))
    return "，".join(desc_parts)


# 1. 布尔型工艺字段 → 描述模板
BOOL_PROCESS_MAP = {
    "是否电弧熔炼": "采用电弧熔炼工艺",
    "是否放电等离子烧结": "采用放电等离子烧结工艺",
    "是否激光熔覆": "采用激光熔覆工艺",
    "是否电火花沉积": "采用电火花沉积工艺",
    "是否定向能量沉积": "采用定向能量沉积工艺",
    "是否退火": "进行了退火处理",
}


def process_dict_to_desc(process: Dict[str, Any]) -> str:
    """
    将工艺 dict 转换为一句自然语言描述
    仅当字段值为 True 时才加入描述
    """
    desc_parts: List[str] = []

    # 1. 处理布尔工艺
    for key, template in BOOL_PROCESS_MAP.items():
        if process.get(key) is True:
            desc_parts.append(template)

    # 2. 处理退火参数（仅在退火=True 时）
    if process.get("是否退火") is True:
        anneal_time = process.get("退火时间(h)")
        anneal_temp = process.get("退火温度(℃)")

        param_parts = []
        if anneal_time is not None:
            param_parts.append(f"{anneal_time} h")
        if anneal_temp is not None:
            param_parts.append(f"{anneal_temp} ℃")

        if param_parts:
            desc_parts.append("退火条件为 " + "，".join(param_parts))

    # 3. 组合成一句话
    if not desc_parts:
        return "未指定处理工艺"

    return "，".join(desc_parts)

def assemble_prompt(payload: Dict[str, Any], phase_result: Dict[str, Any], cal_dict: Dict[str, Any], deep_think: bool) -> str:
    target_name = payload.get("target_property")
    calculate_desc = assemble_calculate_desc(target_name, cal_dict)
    if payload["process"].get("是否激光熔覆", False) and not payload["process"].get("是否电弧熔炼", False):
        process_desc = "采用激光熔覆工艺"
    elif payload["process"].get("是否电弧熔炼", False) and not payload["process"].get("是否激光熔覆", False):
        process_desc = "采用电弧熔炼工艺"
    else:
        process_desc = process_dict_to_desc(payload.get("process", {}))
    
    label = phase_result.get("label", [0, 0, 0])
    phases = [name for i, name in enumerate(['FCC', 'BCC', 'IM']) if label[i] == 1]
    phase_desc = " + ".join(phases) if phases else "None"
    composition = payload.get("composition", {})
    sorted_comp = sorted(composition.items(), key=lambda x: x[1], reverse=True)
    comp_parts = [f"{elem}{int(frac * 100)}" for elem, frac in sorted_comp if frac > 0]
    composition_str = "".join(comp_parts)

    system_prompt, user_prompt = TRAINPROMPTS[target_name]
    think_key = "think" if deep_think else "no_think"
    think_prompt = ThinkPrompts[think_key]
    query = user_prompt.format(
                    calculate_desc=calculate_desc,
                    composition=composition_str,
                    predicted_phases=phase_desc,
                    process_desc=process_desc,
                    think_prompt=think_prompt
                )
    if think_key == "no_think":
        query += "<think>\n\n</think>\n\n"
    
    display_prompt = system_prompt + "\n\n" + query

    original_prompt_temp = PROMPTS[target_name]
    rule = RULES[target_name]
    query_with_know = original_prompt_temp.format(
        Rules=rule,
        sim_HEAs="",
        composition=composition_str,
        process_desc=process_desc,
        calculate_desc=calculate_desc,
        predicted_phases=phase_desc
    )
    prompts = {
        "system_prompt": system_prompt,
        "user_prompt": query,
        "display_prompt": display_prompt,
        "query_with_know": query_with_know
    }
    return prompts