import os
import requests
import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="CarryAura AI Monitor",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 CarryAura AI Monitor")

PRODUCT_URL = "https://carryaura.com/product/product-luna-pebbled-leather-moon-bag/"

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY is not configured.")
    st.stop()

client = Groq(api_key=api_key)

if st.button("🔍 Check Website"):

    try:
        response = requests.get(
            PRODUCT_URL,
            timeout=15,
            headers={
                "User-Agent": "CarryAura-AI-Monitor/1.0"
            }
        )

        status_code = response.status_code

        if 200 <= status_code < 400:
            st.success(f"✅ Website is healthy — HTTP {status_code}")
        else:
            st.error(f"❌ Website returned HTTP {status_code}")

        prompt = f"""
You are a website monitoring assistant.

Website:
{PRODUCT_URL}

HTTP Status:
{status_code}

Give me a simple report:

1. Website status
2. Meaning of the HTTP status
3. Whether there is an obvious problem
4. Recommended next action

Keep it short and easy to understand.
"""

        with st.spinner("🤖 Groq is analyzing..."):

            result = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )

        st.subheader("🤖 AI Analysis")
        st.write(result.choices[0].message.content)

    except requests.RequestException as e:
        st.error(f"❌ Website check failed: {e}")

    except Exception as e:
        st.error(f"❌ Error: {e}")
