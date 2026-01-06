import streamlit as st
from typing import List

def init_state(material_cols: List[str], default_mode: str, model_choices: List[str]):
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant",
             "content": "Hi! Fill in the HEA composition & processing on the left, select a target property, then evaluate on the right."}
        ]

    for e in material_cols:
        st.session_state.setdefault(f"comp_frac_{e}", 0.0)
        st.session_state.setdefault(f"comp_at_{e}", 0.0)

    st.session_state.setdefault("comp_mode", default_mode)

    st.session_state.setdefault("model_name", model_choices[0] if model_choices else "default")

    st.session_state.setdefault("proc_anneal_choice", "Unknown")
    st.session_state.setdefault("proc_anneal_time", None)
    st.session_state.setdefault("proc_anneal_temp", None)
