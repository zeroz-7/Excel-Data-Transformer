import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/transform")  # default to local backend

st.set_page_config(page_title="CrewAI Excel Transformer", layout="wide")
st.title("📊 CrewAI Excel Transformer")

uploaded_files = st.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)
prompt = st.text_area("Enter transformation instructions")

if st.button("Generate Script"):
    if uploaded_files and prompt:
        files = [
            ("files", (f.name, f.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
            for f in uploaded_files
        ]
        try:
            with st.spinner("Generating script..."):
                response = requests.post(API_URL, data={"prompt": prompt}, files=files)
                
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("status") == "success":
                    script = response_data["script"]

                    st.success("✅ Script generated successfully!")
                    st.code(script, language="python")

                    # 🔥 Add download button
                    st.download_button(
                        label="💾 Download Script as .py",
                        data=script,
                        file_name="generated_script.py",
                        mime="text/x-python"
                    )
                else:
                    st.error(f"❌ Backend error: {response_data.get('error', 'Unknown error')}")
            else:
                st.error(f"❌ HTTP error: {response.status_code} {response.text}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")
    else:
        st.error("Please upload at least one file and enter a prompt.")
