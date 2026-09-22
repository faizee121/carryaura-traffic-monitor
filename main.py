import os
import requests
import streamlit as st
from groq import Groq


# ==========================================
# Streamlit Configuration
# ==========================================

st.set_page_config(
    page_title="CarryAura AI Monitor",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 CarryAura AI Monitor")


# ==========================================
# Website
# ==========================================

PRODUCT_URL = (
    "https://carryaura.com/product/"
    "product-luna-pebbled-leather-moon-bag/"
)


# ==========================================
# Groq API
# ==========================================

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY is not configured.")
    st.stop()

client = Groq(
    api_key=api_key
)


# ==========================================
# Website Health Check
# ==========================================

if st.button("🔍 Check Website"):

    try:

        # ----------------------------------
        # Check website
        # ----------------------------------

        response = requests.get(
            PRODUCT_URL,
            timeout=15,
            headers={
                "User-Agent": "CarryAura-AI-Monitor/1.0"
            }
        )

        status_code = response.status_code


        # ----------------------------------
        # Display website status
        # ----------------------------------

        st.subheader("🌐 Website Status")

        if 200 <= status_code < 400:

            st.success(
                f"✅ Website is healthy — HTTP {status_code}"
            )

        else:

            st.error(
                f"❌ Website returned HTTP {status_code}"
            )


        # ----------------------------------
        # Send result to Groq
        # ----------------------------------

        prompt = f"""
You are a website monitoring assistant.

Analyze this website health-check result.

Website:
{PRODUCT_URL}

HTTP Status:
{status_code}

Provide a simple monitoring report with:

1. Website status
2. Meaning of the HTTP status
3. Whether there is an obvious problem
4. Recommended next action

Keep the answer short, practical, and easy to understand.
"""


        with st.spinner("🤖 Groq is analyzing..."):

            result = client.chat.completions.create(

                # Current Groq replacement for
                # llama-3.1-8b-instant
                model="openai/gpt-oss-20b",

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.2,

                # GPT-OSS supports this option
                include_reasoning=False
            )


        # ----------------------------------
        # Display AI result
        # ----------------------------------

        st.subheader("🤖 AI Analysis")

        st.write(
            result.choices[0].message.content
        )


    # ======================================
    # Error Handling
    # ======================================

    except requests.RequestException as e:

        st.error(
            f"❌ Website check failed: {e}"
        )

    except Exception as e:

        st.error(
            f"❌ Groq/API Error: {e}"
        )
