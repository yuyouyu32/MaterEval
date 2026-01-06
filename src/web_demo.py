# web_demo.py
import streamlit as st
import json

from config import MaterialColumns, ProcessColumnsEn, TargetProps

from ui.styles import inject_styles, render_header
from ui.state import init_state

from ui.composition import (
    render_composition_card,
    validate_composition,
    composition_sum_fraction,
    composition_sum_at,
)
from ui.processing import render_processing_card, build_process_from_state
from ui.target import render_target_card
from ui.model_selector import render_model_selector
from ui.chat import render_chat_panel

from backend.llm_client import build_payload, call_llm
from backend.cls_client import phase_predictor


ModelChoices = ["DeepSeek-R1-0628", "Qwen3-8B-MaterEval"]

st.set_page_config(page_title="HEA Evaluator", page_icon="🧪", layout="wide", initial_sidebar_state="collapsed")

inject_styles()
render_header()

# init all needed session_state keys
init_state(MaterialColumns, default_mode="at.% (0–100)", model_choices=ModelChoices)

left, right = st.columns([0.48, 0.52], gap="large")

with left:
    # 1) composition -> comp_frac
    comp_frac = render_composition_card(MaterialColumns)

    # 2) processing UI (renders widgets)
    _process_ui = render_processing_card(ProcessColumnsEn)

    # 3) target selection
    target = render_target_card(TargetProps)

    # 4) snapshot (IMPORTANT: rebuild process from session_state)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">4) Input snapshot</div>', unsafe_allow_html=True)

    comp_nonzero = {k: float(v) for k, v in comp_frac.items() if float(v) > 0}
    process_snapshot = build_process_from_state()

    st.code(
        json.dumps(build_payload(comp_nonzero, process_snapshot, target), ensure_ascii=False, indent=2),
        language="json",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    # model selector on the right
    model_name, deep_think = render_model_selector(ModelChoices)


    def validator() -> bool:
        return validate_composition(st.session_state["comp_mode"], MaterialColumns)

    def invalid_msg() -> str:
        if st.session_state["comp_mode"].startswith("Fraction"):
            s = composition_sum_fraction(MaterialColumns)
            return f"❌ Composition sum must be 1.0. Current sum = {s:.4f}. Please adjust or click Normalize."
        s = composition_sum_at(MaterialColumns)
        return f"❌ Composition sum must be 100.0 (at.%). Current sum = {s:.2f}. Please adjust or click Normalize."

    def payload_builder():
        # ✅ always rebuild process from state at call time
        return build_payload(comp_frac, build_process_from_state(), target)

    render_chat_panel(
        model_name=model_name,
        target=target,
        payload_builder=payload_builder,
        validator=validator,
        invalid_message_builder=invalid_msg,
        llm_caller=call_llm,
        phase_predictor=phase_predictor,
        deep_think=deep_think,
)

st.markdown('<div class="footer-note">Developed by Lab 106 @ SHU | © 2026</div>', unsafe_allow_html=True)
