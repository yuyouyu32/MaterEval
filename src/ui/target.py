import streamlit as st
from typing import List

def render_target_card(target_props: List[str]) -> str:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">3) Target property</div>', unsafe_allow_html=True)
    target = st.radio("Choose one", target_props, index=0, horizontal=True, label_visibility="collapsed")
    st.markdown(f'<span class="pill">Target: <b>{target}</b></span>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    return target
