import streamlit as st
from workiq_connector import build_context_package
from meeting_intelligence import generate, extract_topic_keywords

st.set_page_config(page_title="MeetMind", page_icon="🧠", layout="wide")

st.title("🧠 MeetMind")
st.caption("Context-aware meeting intelligence, powered by Work IQ")

st.markdown("### 1. Paste or load a meeting transcript")

default_transcript = ""
try:
    with open("sample_transcript.txt", "r") as f:
        default_transcript = f.read()
except FileNotFoundError:
    pass

transcript = st.text_area(
    "Meeting transcript",
    value=default_transcript,
    height=250,
)

if st.button("Run MeetMind", type="primary"):
    if not transcript.strip():
        st.warning("Please provide a transcript first.")
    else:
        with st.spinner("Querying Work IQ for relevant context..."):
            keywords = extract_topic_keywords(transcript)
            context_package = build_context_package(keywords)

        with st.expander("📡 Work IQ Context Retrieved", expanded=False):
            st.json(context_package)

        with st.spinner("Running post-meeting reasoning engine..."):
            result = generate(transcript, context_package)

        if "error" in result:
            st.error("Something went wrong generating the output.")
            st.code(result.get("raw", ""))
        else:
            st.markdown("### 2. 📋 3-Sentence Decision Log")
            dl = result["decision_log"]
            st.info(f"**Context:** {dl['context']}")
            st.success(f"**Resolution:** {dl['resolution']}")
            st.warning(f"**Forward Trajectory:** {dl['forward_trajectory']}")

            st.markdown("### 3. ✅ Smart Action Items")
            for item in result["action_items"]:
                with st.container(border=True):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown(f"**{item['assignee_name']}**")
                        st.caption(item.get("assignee_email", ""))
                    with col2:
                        st.markdown(item["task"])
                        st.caption(f"Due: {item.get('due_context', 'Not specified')}")
                        if item.get("linked_context", "None") != "None":
                            st.caption(f"🔗 {item['linked_context']}")

            st.markdown("### 4. ✉️ Drafted Follow-Up Emails")
            for email in result["follow_up_emails"]:
                with st.expander(f"To: {email['to_name']} — {email['subject']}"):
                    st.text(email["body"])
                    st.caption(
                        "✅ Saved to Outlook Drafts folder "
                        "(simulated — human review required before sending)"
                    )

st.divider()
st.caption(
    "MeetMind operates within the Microsoft 365 Copilot ecosystem. "
    "All outputs are placed in Drafts for human review — no automated "
    "sending, ensuring compliance and zero unintended data exposure."
)