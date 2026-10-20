import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="ScamGuard", page_icon="???")

st.title("??? ScamGuard")
st.write("Semak mesej, pautan, atau akaun bank yang mencurigakan. / Check a suspicious message, link, or bank account.")

# Stats Counter
try:
    stats = requests.get(f"{API_URL}/api/stats").json()
    st.caption(f"Protected users from **{stats['total_checks']}** suspicious messages so far.")
except:
    pass

lang = st.radio("Language / Bahasa", options=["ms", "en"], horizontal=True)
input_text = st.text_area("Paste message here / Tampal mesej di sini:", height=150)
uploaded_image = st.file_uploader("Or upload a screenshot / Atau muat naik tangkap layar (OCR coming soon)", type=["png", "jpg", "jpeg"])

if st.button("Check / Semak", type="primary"):
    if input_text or uploaded_image:
        with st.spinner("Analyzing..."):
            files = {}
            data = {"lang": lang}
            
            if input_text:
                data["text"] = input_text
            if uploaded_image:
                files["image"] = (uploaded_image.name, uploaded_image, uploaded_image.type)
                
            res = requests.post(f"{API_URL}/api/check", data=data, files=files if files else None)
            
            if res.status_code == 200:
                verdict = res.json()
                
                # Verdict Colors
                color_map = {"DANGER": "red", "CAUTION": "orange", "SAFE": "green"}
                color = color_map.get(verdict["level"], "grey")
                
                # Large Coloured Verdict Card
                st.markdown(f"""
                <div style="background-color: {color}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                    <h2>{verdict["level"]} (Score: {verdict["score"]})</h2>
                    <p style="font-size: 18px;"><b>{verdict["advice"]}</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("### Reasons / Sebab:")
                for reason in verdict["reasons"]:
                    st.write(f"- {reason}")
                
                # Report Button Logic
                if verdict["level"] in ["DANGER", "CAUTION"]:
                    st.write("---")
                    st.write("Help others by reporting this scam pattern / Bantu orang lain dengan melaporkan corak penipuan ini:")
                    
                    if st.button("?? Report to Database"):
                        # Just reporting the text as an example for MVP
                        report_data = {
                            "value": input_text[:50], 
                            "entity_type": "message",
                            "scam_type": verdict["scam_type"]
                        }
                        r_res = requests.post(f"{API_URL}/api/report", json=report_data)
                        if r_res.status_code == 200:
                            st.success(f"Reported successfully! Total flags: {r_res.json()['report_count']}")
            else:
                st.error("Error connecting to the engine.")
    else:
        st.warning("Please provide text or an image.")