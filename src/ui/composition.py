import streamlit as st
from typing import Dict, List
import math

DEFAULT_COMPOSITION_FRAC = {
    "Co": 0.24,
    "Cr": 0.24,
    "Fe": 0.24,
    "Ni": 0.24,
    "Mo": 0.04,
}

def is_close(a: float, b: float, eps: float = 1e-6) -> bool:
    return abs(a - b) <= eps

def sync_at_from_frac(material_cols: List[str]):
    for e in material_cols:
        st.session_state[f"comp_at_{e}"] = float(st.session_state[f"comp_frac_{e}"]) * 100.0

def sync_frac_from_at(material_cols: List[str]):
    for e in material_cols:
        st.session_state[f"comp_frac_{e}"] = float(st.session_state[f"comp_at_{e}"]) / 100.0

def normalize_callback(material_cols: List[str]):
    mode = st.session_state["comp_mode"]
    if mode.startswith("Fraction"):
        total = sum(float(st.session_state[f"comp_frac_{e}"]) for e in material_cols)
        if total <= 0:
            st.toast("Nothing to normalize (sum is 0).", icon="⚠️")
            return
        for e in material_cols:
            st.session_state[f"comp_frac_{e}"] = float(st.session_state[f"comp_frac_{e}"]) / total
        sync_at_from_frac(material_cols)
    else:
        total = sum(float(st.session_state[f"comp_at_{e}"]) for e in material_cols)
        if total <= 0:
            st.toast("Nothing to normalize (sum is 0).", icon="⚠️")
            return
        for e in material_cols:
            st.session_state[f"comp_at_{e}"] = float(st.session_state[f"comp_at_{e}"]) / total * 100.0
        sync_frac_from_at(material_cols)

def clear_callback(material_cols: List[str]):
    for e in material_cols:
        st.session_state[f"comp_frac_{e}"] = 0.0
        st.session_state[f"comp_at_{e}"] = 0.0

def composition_fraction_view(material_cols: List[str]) -> Dict[str, float]:
    return {e: float(st.session_state[f"comp_frac_{e}"]) for e in material_cols}

def composition_sum_fraction(material_cols: List[str]) -> float:
    return sum(float(st.session_state[f"comp_frac_{e}"]) for e in material_cols)

def composition_sum_at(material_cols: List[str]) -> float:
    return sum(float(st.session_state[f"comp_at_{e}"]) for e in material_cols)

def validate_composition(mode: str, material_cols: List[str]) -> bool:
    if mode.startswith("Fraction"):
        return is_close(composition_sum_fraction(material_cols), 1.0, eps=1e-3)
    return is_close(composition_sum_at(material_cols), 100.0, eps=1e-2)

def render_composition_card(material_cols: List[str]):
    # ✅ 1. inject default composition ONCE
    if "composition_initialized" not in st.session_state:
        for e in material_cols:
            frac = DEFAULT_COMPOSITION_FRAC.get(e, 0.0)
            st.session_state[f"comp_frac_{e}"] = frac
            st.session_state[f"comp_at_{e}"] = frac * 100.0
        st.session_state["composition_initialized"] = True
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">1) Composition</div>', unsafe_allow_html=True)

    mode = st.radio(
        "Input mode",
        ["at.% (0–100)", "Fraction (0–1)"],
        horizontal=True,
        key="comp_mode",
        label_visibility="collapsed",
        on_change=lambda: (sync_at_from_frac(material_cols) if st.session_state["comp_mode"].startswith("at.%")
                           else sync_frac_from_at(material_cols)),
    )

    st.markdown(
        '<div class="hint">'
        'Choose <b>at.%</b> to input percentages (auto converted to fractions). '
        'Use <b>Normalize</b> if the sum is off.'
        '</div>',
        unsafe_allow_html=True
    )

    with st.form("composition_form", clear_on_submit=False):
        cols = st.columns(5)

        if mode.startswith("Fraction"):
            for i, elem in enumerate(material_cols):
                with cols[i % 5]:
                    st.number_input(elem, min_value=0.0, max_value=1.0, step=0.01, format="%.4f", key=f"comp_frac_{elem}")
            total = composition_sum_fraction(material_cols)
            if is_close(total, 1.0, 1e-3):
                st.success(f"Sum = {total:.4f} ✅ (target = 1.0000)")
            else:
                st.warning(f"Sum = {total:.4f} (target = 1.0000)")
        else:
            for i, elem in enumerate(material_cols):
                with cols[i % 5]:
                    st.number_input(elem, min_value=0.0, max_value=100.0, step=0.5, format="%.2f", key=f"comp_at_{elem}")
            total = composition_sum_at(material_cols)
            if is_close(total, 100.0, 1e-2):
                st.success(f"Sum = {total:.2f} ✅ (target = 100.00)")
            else:
                st.warning(f"Sum = {total:.2f} (target = 100.00)")

        b1, b2, _ = st.columns([1, 1, 2])
        with b1:
            st.form_submit_button("Normalize", use_container_width=True, on_click=normalize_callback, args=(material_cols,))
        with b2:
            st.form_submit_button("Clear", use_container_width=True, on_click=clear_callback, args=(material_cols,))
        st.caption("Backend always receives fractions (0–1).")

    st.markdown("</div>", unsafe_allow_html=True)

    # after widgets, keep frac in sync for payload
    if mode.startswith("at.%"):
        sync_frac_from_at(material_cols)
    else:
        sync_at_from_frac(material_cols)

    return composition_fraction_view(material_cols)
