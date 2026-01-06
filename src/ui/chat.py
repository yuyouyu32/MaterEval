import streamlit as st
from typing import Dict, Any, Callable, Any as AnyType, Iterator, Tuple
from backend.assemble_prompt import assemble_prompt


# stream item: ("think" | "final", chunk)
StreamItem = Tuple[str, str]


def render_chat_panel(
    model_name: str,
    target: str,
    payload_builder: Callable[[], Dict[str, Any]],
    validator: Callable[[], bool],
    invalid_message_builder: Callable[[], str],
    llm_caller: Callable[[str, Dict[str, str], Dict[str, Any], bool], Iterator[StreamItem]],
    phase_predictor: AnyType,  # expects .predict_one(payload) -> (phase_result, calc_dict)
    deep_think: bool = True,
):
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💬 Chat with the Evaluation LLM</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hint">Chat freely, or click <b>One-click Evaluate</b> to run without typing.</div>',
        unsafe_allow_html=True,
    )

    # ── Buttons row ─────────────────────────────
    b1, b2, b3 = st.columns([1.2, 1.2, 2.6])
    with b1:
        one_click = st.button("⚡ One-click Evaluate", use_container_width=True)
    with b2:
        clear_chat = st.button("🧹 Clear Chat", use_container_width=True)
    with b3:
        st.caption("Evaluate with current inputs, or clear all chat history.")

    # ── Clear chat logic ───────────────────────
    if clear_chat:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "🧪 Chat cleared. Fill inputs on the left and evaluate again when ready.",
            }
        ]
        # also clear any pending generation
        st.session_state.pop("__pending_stream__", None)
        st.rerun()

    # ── Render history ─────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    def run_eval(user_prompt: str):
        if not validator():
            st.session_state.messages.append(
                {"role": "assistant", "content": invalid_message_builder()}
            )
            st.rerun()

        payload = payload_builder()
        phase_result, calc_dict = phase_predictor.predict_one(payload)

        prompts: Dict[str, str] = assemble_prompt(payload, phase_result, calc_dict, deep_think)

        # display_prompt for user-visible "what we are asking the model to do"
        display_prompt = prompts.get("display_prompt", "")
        if user_prompt.strip():
            display_prompt += f"\n\nUser question: {user_prompt}"

        # 1) push user message to history
        st.session_state.messages.append({"role": "user", "content": display_prompt})

        # 2) stash pending streaming job (so next rerun shows user message first)
        st.session_state["__pending_stream__"] = {
            "model_name": model_name,
            "prompts": prompts,
            "payload": payload,
            "deep_think": deep_think,
        }
        st.rerun()

    # One-click evaluation: run without extra user text
    if one_click:
        run_eval("")

    # ── Pending streaming generation ───────────
    pending = st.session_state.pop("__pending_stream__", None)
    if pending is not None:
        final_buf = ""
        think_buf = ""

        with st.chat_message("assistant"):
            # collapsible think box (only show if deep_think is enabled)
            if pending.get("deep_think", True):
                with st.expander("🧠 Deep Think (click to expand)", expanded=True):
                    think_placeholder = st.empty()
            else:
                think_placeholder = None

            final_placeholder = st.empty()

            try:
                stream = llm_caller(
                    pending["model_name"],
                    pending["prompts"],
                    pending["payload"],
                    pending["deep_think"],
                )

                for tag, chunk in stream:
                    if not chunk:
                        continue

                    if tag == "think":
                        # show only, do NOT write to history
                        if think_placeholder is not None:
                            think_buf += chunk
                            think_placeholder.markdown(
                                f"""
                                <div style="
                                    background-color:#f3f4f6;
                                    color:#4b5563;
                                    padding:10px;
                                    border-radius:10px;
                                    font-size:13px;
                                    line-height:1.45;
                                    white-space:pre-wrap;
                                ">{think_buf}</div>
                                """,
                                unsafe_allow_html=True,
                            )
                        # if deep_think disabled or placeholder absent, ignore think

                    elif tag == "final":
                        final_buf += chunk
                        final_placeholder.markdown(final_buf)

                    else:
                        # unknown tag -> treat as final for robustness
                        final_buf += chunk
                        final_placeholder.markdown(final_buf)

            except Exception as e:
                final_buf = f"❌ LLM call failed: {e}"
                final_placeholder.markdown(final_buf)

        # ✅ history: ONLY final (no think)
        st.session_state.messages.append({"role": "assistant", "content": final_buf})
        st.rerun()

    # ── User input ─────────────────────────────
    prompt = st.chat_input("Type your message (e.g., 'Evaluate corrosion potential and give a score.')")
    if prompt:
        run_eval(prompt)

    st.markdown("</div>", unsafe_allow_html=True)
