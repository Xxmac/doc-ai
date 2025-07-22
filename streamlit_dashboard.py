import streamlit as st
import requests

st.set_page_config(page_title="Doctor Appointment Assistant", page_icon="💊", layout="centered")
st.title("💉 Doctor Appointment Assistant")
st.markdown("**Ask about doctor availability:**")

query = st.text_input("Type your question here...")

if st.button("Submit") and query.strip():
    with st.spinner("Thinking..."):
        try:
            response = requests.post("http://localhost:8000/ask", json={"query": query})
            if response.status_code == 200:
                data = response.json()
                st.markdown("### SQL Query Used:")
                st.code(data["sql_query"], language="sql")

                st.markdown("### Answer:")
                st.success(data["response"])
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
