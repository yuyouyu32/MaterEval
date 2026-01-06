# ui/model_selector.py
import streamlit as st
from typing import List, Tuple


def render_model_selector(model_choices: List[str]) -> Tuple[str, bool]:
    """
    Returns:
        model_name (str): selected model
        deep_think (bool): whether deep thinking mode is enabled
    """

    # defaults
    st.session_state.setdefault("model_name", model_choices[0] if model_choices else "default")
    st.session_state.setdefault("deep_think", True)   # ✅ default ON

    c1, c2 = st.columns([1.3, 2.7])

    with c1:
        model_name = st.selectbox(
            "Model",
            model_choices,
            key="model_name",
        )

    with c2:
        deep_think = st.checkbox(
            "Deep Think",
            key="deep_think",
            help="Enable slow / reasoning-intensive evaluation (think mode).",
        )

    st.caption("Model & reasoning mode are chosen here and only passed when calling the backend.")

    return model_name, deep_think
