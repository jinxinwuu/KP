import os
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Kill Procrastination", layout="centered")
st.title("Kill Procrastination")

# ────────────────────────────────────────────────
# Session state initialization
# ────────────────────────────────────────────────
defaults = {
    "goal": "",
    "step": None,
    "history": [],
    "doing_now": False,
    "finished": False,
    "streak": 0,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


def clean_step_text(text: str) -> str:
    """Remove common prefixes and extra whitespace"""
    prefixes = ["First step:", "Tiny step:", "Next step:", "Step:"]
    cleaned = text.strip()
    for p in prefixes:
        if cleaned.lower().startswith(p.lower()):
            cleaned = cleaned[len(p):].strip()
    return cleaned


def looks_dangerous(goal: str) -> bool:
    """Very basic safety check — expand later if needed"""
    danger_keywords = ["kill", "hurt", "suicide", "self-harm", "cut", "poison", "jump off"]
    return any(kw in goal.lower() for kw in danger_keywords)


# ────────────────────────────────────────────────
# Prompt templates (the most important part)
# ────────────────────────────────────────────────

FIRST_STEP_PROMPT = """\
You are the best procrastination-killer coach.  
Your ONLY job: help the user START right now with ONE tiny, concrete action.

Rules — you MUST follow ALL of them:
- One single physical or digital micro-action
- Takes < 90 seconds (ideally < 30s)
- Zero decisions left to make
- Names exact object/tool/location/app/file
- Has a clear stopping point
- Removes almost all starting friction
- Advances the goal — never trivial or meaningless
- Never: "think about", "decide", "plan", "research", "learn about"
- Tone: calm supportive friend — short & direct

Goal: {goal}

Output ONLY in this exact format (nothing else):

Tiny step: <one very clear sentence>

Why it helps: <one short calm sentence>
"""

SMALLER_PROMPT = """\
The user still feels too much resistance.

Current step: {current}

Make it **significantly smaller** and easier while still meaningfully moving toward the goal.
Follow the same strict rules as above.

Output ONLY:

Tiny step: <one even smaller clear sentence>

Why it helps: <short calm explanation>
"""

NEXT_STEP_PROMPT = """\
You are helping the user build momentum — one tiny win at a time.

Goal: {goal}

Previous completed micro-steps (in order):
{history_text}

Rules — must obey ALL:
- Next action builds **directly** on the most recent completed step
- Never repeat, go backwards, or restart earlier
- One concrete micro-action (< 2 min)
- Specific object/tool/file/location/app
- Clear start + clear stop
- Avoids: "learn about", "find", "research", "plan", "decide"
- Slightly more advanced than last step — but still very easy to begin
- No trivial filler actions

Output ONLY:

Tiny step: <one clear next micro-action>

Why it helps: <one short encouraging sentence>
"""


def generate_with_retry(prompt_template: str, **kwargs) -> str:
    full_prompt = prompt_template.format(**kwargs)
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.25,
                max_tokens=180,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            if attempt == 2:
                st.error(f"API error after 3 tries: {e}")
                return "Sorry — something went wrong with the step generator."
            continue


# ────────────────────────────────────────────────
# UI Flow
# ────────────────────────────────────────────────

goal_input = st.text_input(
    "What do you want to start today?",
    value=st.session_state.goal,
    placeholder="e.g. write my thesis, get fit, learn Python",
    key="goal_input"
)

if st.button("→ Start", type="primary", use_container_width=True):
    new_goal = goal_input.strip()
    if not new_goal:
        st.warning("Please enter a goal first.")
        st.stop()

    if looks_dangerous(new_goal):
        st.error("This goal sounds serious or unsafe. I can't help with that — please reach out to someone you trust or a professional support line.")
        st.stop()

    # Reset for new goal
    st.session_state.goal = new_goal
    st.session_state.history = []
    st.session_state.step = None
    st.session_state.doing_now = False
    st.session_state.finished = False
    st.session_state.streak = 0

    # Generate first step
    with st.spinner("Finding the tiniest possible first step…"):
        st.session_state.step = generate_with_retry(
            FIRST_STEP_PROMPT,
            goal=new_goal
        )
    st.rerun()


# ─── Main screen after goal is set ────────────────────────────────

if st.session_state.goal:

    st.subheader(f"Goal: {st.session_state.goal}")

    # Show history
    if st.session_state.history:
        st.caption("What you've already done:")
        for i, past in enumerate(st.session_state.history, 1):
            st.write(f"✓ {clean_step_text(past)}")

    # Current step
    if st.session_state.step:
        clean_step = clean_step_text(st.session_state.step)

        st.markdown("**Tiny step right now:**")
        st.info(clean_step)

        col1, col2 = st.columns(2)

        if not st.session_state.doing_now and not st.session_state.finished:
            if col1.button("Do it now", use_container_width=True):
                st.session_state.doing_now = True
                st.rerun()

            if col2.button("Make it smaller", use_container_width=True):
                with st.spinner("Shrinking it even more…"):
                    smaller = generate_with_retry(
                        SMALLER_PROMPT,
                        current=clean_step
                    )
                    st.session_state.step = smaller
                st.rerun()

    # Doing now state
    if st.session_state.doing_now and not st.session_state.finished:
        st.success("Nice. Go do it right now.  \nI'll wait here — no pressure.")
        if st.button("I finished this tiny step", type="primary"):
            st.session_state.history.append(st.session_state.step)
            st.session_state.streak += 1
            st.session_state.finished = True
            st.session_state.doing_now = False
            st.rerun()

    # Finished state
    if st.session_state.finished:
        messages = [
            "One tiny win counts. Seriously. Great job showing up.",
            "You did the thing. Momentum is building. See you tomorrow?",
            "Small step → big change. Proud of you for starting.",
            "That's how it happens — one micro-action at a time. Rest well."
        ]
        import random
        st.success(random.choice(messages))

        if st.button("→ Next tiny step", type="primary", use_container_width=True):
            with st.spinner("Preparing the next small win…"):
                history_clean = [clean_step_text(s) for s in st.session_state.history]
                history_str = "\n- " + "\n- ".join(history_clean) if history_clean else "(nothing yet)"

                next_step = generate_with_retry(
                    NEXT_STEP_PROMPT,
                    goal=st.session_state.goal,
                    history_text=history_str
                )
                st.session_state.step = next_step
                st.session_state.finished = False
            st.rerun()

st.caption("v0.2 • one tiny step at a time")


