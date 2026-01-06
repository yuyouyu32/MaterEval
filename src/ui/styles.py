import streamlit as st

CSS = """
<style>
  .app-title { font-size: 28px; font-weight: 750; letter-spacing: 0.2px; margin-bottom: 2px; }
  .app-subtitle { color: rgba(0,0,0,0.65); font-size: 14px; margin-top: 0px; margin-bottom: 12px; }
  .section-card {
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 16px;
    padding: 14px 14px 6px 14px;
    background: rgba(255,255,255,0.7);
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
    margin-bottom: 12px;
  }
  .section-title { font-weight: 700; font-size: 15px; margin-bottom: 8px; }
  .hint { color: rgba(0,0,0,0.6); font-size: 12px; margin-top: -6px; margin-bottom: 8px; }
  .pill {
    display: inline-block; padding: 2px 10px; border-radius: 999px;
    border: 1px solid rgba(0,0,0,0.12); font-size: 12px; margin-right: 6px; margin-bottom: 6px;
    background: rgba(0,0,0,0.02);
  }
  .chat-wrap {
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 16px;
    padding: 10px 10px 2px 10px;
    background: rgba(255,255,255,0.7);
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
  }
  .footer-note { color: rgba(0,0,0,0.5); font-size: 12px; }
  .small-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
                font-size: 12px; color: rgba(0,0,0,0.65); }
  .mini-divider { height: 10px; }
</style>
"""

def inject_styles():
    st.markdown(CSS, unsafe_allow_html=True)

def render_header():
    st.markdown('<div class="app-title">🧪 HEA Evaluation Playground</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Input composition + processing, choose a target property, pick a model, and evaluate.</div>',
        unsafe_allow_html=True
    )
