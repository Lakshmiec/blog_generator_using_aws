import streamlit as st
import requests
import json

# Replace this with your actual API Gateway endpoint
API_ENDPOINT = "https://oqvms0bstc.execute-api.us-east-1.amazonaws.com/dev_env/blog-generation"

st.title("📝 AI Blog Generator")

# Input field for blog topic
blog_topic = st.text_input("Enter a blog topic")

# Button to generate blog
if st.button("Generate Blog"):
    if not blog_topic.strip():
        st.warning("Please enter a topic first.")
    else:
        with st.spinner("Generating blog..."):
            try:
                # Make POST request to your API Gateway
                payload = {"blog_topic": blog_topic}
                response = requests.post(API_ENDPOINT, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    blog_text = result.get("blog", "")
                    st.success("Blog generated successfully!")
                    st.text_area("Generated Blog", blog_text, height=300)
                    st.download_button("📥 Download Blog", blog_text, file_name="generated_blog.txt")
                else:
                    st.error(f"Failed: {response.status_code} - {response.text}")

            except Exception as e:
                st.error(f"Error: {e}")
