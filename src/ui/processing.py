# ui/processing.py
import streamlit as st
from typing import Dict, Any, Optional
import math


def sanitize_float(x: Optional[float]) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    return float(x)


def render_processing_card(process_columns_en: Dict[str, str]) -> Dict[str, Any]:
    """
    Render the processing UI and return a process dict.
    Note: For snapshot/payload, prefer build_process_from_state() to avoid st rerun timing issues.
    """
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">2) Processing</div>', unsafe_allow_html=True)
    st.markdown('<div class="hint">Annealing time/temperature appear only when Annealing = Yes.</div>',
                unsafe_allow_html=True)

    yn_map = {"Unknown": None, "No": False, "Yes": True}
    process: Dict[str, Any] = {}

    # Row 1
    r1 = st.columns(3)
    with r1[0]:
        k = "是否电弧熔炼"
        v = st.selectbox(process_columns_en[k], list(yn_map.keys()), index=2, key="proc_arc")
        process[k] = yn_map[v]
    with r1[1]:
        k = "是否放电等离子烧结"
        v = st.selectbox(process_columns_en[k], list(yn_map.keys()), index=0, key="proc_sps")
        process[k] = yn_map[v]
    with r1[2]:
        k = "是否激光熔覆"
        v = st.selectbox(process_columns_en[k], list(yn_map.keys()), index=0, key="proc_laser")
        process[k] = yn_map[v]

    # Row 2
    r2 = st.columns(3)
    with r2[0]:
        k = "是否电火花沉积"
        v = st.selectbox(process_columns_en[k], list(yn_map.keys()), index=0, key="proc_eds")
        process[k] = yn_map[v]
    with r2[1]:
        k = "是否定向能量沉积"
        v = st.selectbox(process_columns_en[k], list(yn_map.keys()), index=0, key="proc_ded")
        process[k] = yn_map[v]
    with r2[2]:
        k = "是否退火"
        anneal_choice = st.selectbox(process_columns_en[k], list(yn_map.keys()), index=0, key="proc_anneal_choice")
        process[k] = yn_map[anneal_choice]

    anneal_enabled = (anneal_choice == "Yes")

    # Hide fields when not annealing
    if not anneal_enabled:
        st.session_state["proc_anneal_time"] = None
        st.session_state["proc_anneal_temp"] = None
        process["退火时间(h)"] = None
        process["退火温度(℃)"] = None
    else:
        st.markdown('<div class="mini-divider"></div>', unsafe_allow_html=True)
        sub = st.columns(2)

        with sub[0]:
            tt = st.number_input(
                process_columns_en["退火温度(℃)"],
                value=st.session_state.get("proc_anneal_temp", None),
                min_value=0.0,
                step=100.0,
                format="%.1f",
                key="proc_anneal_temp",
            )
            process["退火温度(℃)"] = sanitize_float(tt)
        with sub[1]:
            t = st.number_input(
                process_columns_en["退火时间(h)"],
                value=st.session_state.get("proc_anneal_time", None),
                min_value=0.0,
                step=0.5,
                format="%.2f",
                key="proc_anneal_time",
            )
            process["退火时间(h)"] = sanitize_float(t)

    st.markdown("</div>", unsafe_allow_html=True)
    return process


def build_process_from_state() -> Dict[str, Any]:
    """
    Build a process dict purely from st.session_state.
    This avoids 'snapshot shows null but UI has value' timing issues.
    """
    yn_map = {"Unknown": None, "No": False, "Yes": True}

    arc = st.session_state.get("proc_arc", "Unknown")
    sps = st.session_state.get("proc_sps", "Unknown")
    laser = st.session_state.get("proc_laser", "Unknown")
    eds = st.session_state.get("proc_eds", "Unknown")
    ded = st.session_state.get("proc_ded", "Unknown")
    anneal_choice = st.session_state.get("proc_anneal_choice", "Unknown")

    anneal_enabled = (anneal_choice == "Yes")

    proc: Dict[str, Any] = {
        "是否电弧熔炼": yn_map.get(arc, None),
        "是否放电等离子烧结": yn_map.get(sps, None),
        "是否激光熔覆": yn_map.get(laser, None),
        "是否电火花沉积": yn_map.get(eds, None),
        "是否定向能量沉积": yn_map.get(ded, None),
        "是否退火": yn_map.get(anneal_choice, None),
        "退火时间(h)": None,
        "退火温度(℃)": None,
    }

    if anneal_enabled:
        proc["退火时间(h)"] = sanitize_float(st.session_state.get("proc_anneal_time", None))
        proc["退火温度(℃)"] = sanitize_float(st.session_state.get("proc_anneal_temp", None))

    return proc
