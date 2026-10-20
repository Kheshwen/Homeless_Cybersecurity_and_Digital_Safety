import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="ScamGuard", page_icon="🛡️")
st.title("🛡️ ScamGuard")
st.write(
    "Semak mesej, pautan, atau akaun bank yang mencurigakan. / "
    "Check a suspicious message, link, or bank account."
)

# Stats Counter
try:
    stats = requests.get(f"{API_URL}/api/stats", timeout=3).json()
    st.caption(f"Protected users from **{stats['total_checks']}** suspicious messages so far.")
except Exception:
    pass

lang = st.radio("Language / Bahasa", options=["ms", "en"], horizontal=True)
input_text = st.text_area("Paste message here / Tampal mesej di sini:", height=150)
uploaded_image = st.file_uploader(
    "Or upload a screenshot / Atau muat naik tangkap layar:", 
    type=["png", "jpg", "jpeg"]
)

# Trigger analysis and store the result in session state
if st.button("Check / Semak", type="primary"):
    if input_text or uploaded_image:
        with st.spinner("Analyzing..."):
            files = {}
            data = {"lang": lang}

            if input_text:
                data["text"] = input_text
            if uploaded_image:
                files["image"] = (uploaded_image.name, uploaded_image.getvalue(), uploaded_image.type)

            try:
                res = requests.post(
                    f"{API_URL}/api/check", 
                    data=data, 
                    files=files if files else None,
                    timeout=15
                )

                if res.status_code == 200:
                    st.session_state["verdict"] = res.json()
                    st.session_state["analyzed_text"] = input_text or (uploaded_image.name if uploaded_image else "")
                    st.session_state["reported"] = False
                else:
                    st.error(f"Error connecting to the engine (Status code: {res.status_code}).")
            except Exception as e:
                st.error(f"Failed to reach API server: {e}")
    else:
        st.warning("Please provide text or an image.")

# Render persistent results outside the Check button block
if "verdict" in st.session_state:
    verdict = st.session_state["verdict"]

    # Verdict Colors
    color_map = {
        "DANGER": "#D32F2F",   # Red
        "CAUTION": "#F57C00",  # Orange
        "SAFE": "#388E3C",     # Green
        "UNSURE": "#616161"    # Grey
    }
    color = color_map.get(verdict.level, "#616161")

    # Coloured Verdict Card
    st.markdown(
        f"""
        <div style="background-color: {color}; padding: 20px; border-radius: 10px; color: white; text-align: center; margin: 15px 0;">
            <h2 style="color: white; margin: 0;">{verdict['level']} (Score: {verdict['score']})</h2>
            <p style="font-size: 18px; margin-top: 10px;"><b>{verdict['advice']}</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("### Reasons / Sebab:")
    if verdict.get("reasons"):
        for reason in verdict["reasons"]:
            st.write(f"- {reason}")
    else:
        st.write("- No immediate high-risk indicators detected.")

    # Extracted Entities Display
    entities = verdict.get("entities", {})
    detected = []
    if entities.get("accounts"):
        detected.append(f"**Bank Accounts:** {', '.join(entities['accounts'])}")
    if entities.get("phones"):
        detected.append(f"**Phone Numbers:** {', '.join(entities['phones'])}")
    if entities.get("urls"):
        detected.append(f"**Links:** {', '.join(entities['urls'])}")

    if detected:
        st.write("---")
        st.write("### Detected Entities / Entiti Dikesan:")
        for item in detected:
            st.markdown(f"- {item}")

    # Crowdsourced Reporting Block
    if verdict["level"] in ["DANGER", "CAUTION"]:
        st.write("---")
        st.write("Help others by reporting this scam pattern / Bantu orang lain dengan melaporkan corak penipuan ini:")

        if st.session_state.get("reported"):
            st.success("✅ Reported successfully! Thank you for protecting the community.")
        else:
            if st.button("🚨 Report to Database"):
                report_text = st.session_state.get("analyzed_text", "Unknown message")
                report_data = {
                    "value": report_text[:100],
                    "entity_type": "message",
                    "scam_type": verdict.get("scam_type", "other")
                }
                try:
                    r_res = requests.post(f"{API_URL}/api/report", json=report_data, timeout=5)
                    if r_res.status_code == 200:
                        st.session_state["reported"] = True
                        st.rerun()
                    else:
                        st.error("Failed to submit report. Please try again.")
                except Exception as e:
                    st.error(f"Error reporting: {e}")
