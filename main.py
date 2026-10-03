import os
import requests
import streamlit as st
from groq import Groq


# ==========================================
# Email Alert Configuration (Resend)
# ==========================================

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

# Comma-separated list of recipients
ALERT_TO_EMAIL = os.environ.get(
    "ALERT_TO_EMAIL",
    "mfaizee316@gmail.com,hamza.tariq.it@gmail.com"
)

ALERT_FROM_EMAIL = "onboarding@resend.dev"


def send_email_alert(subject: str, html_body: str) -> bool:
    """
    Send an alert email via Resend API to multiple recipients.
    Returns True on success, False on failure.
    Never raises — email failure won't crash the app.
    """
    if not RESEND_API_KEY:
        st.warning("⚠️ RESEND_API_KEY not configured — email not sent.")
        return False

    recipients = [
        email.strip()
        for email in ALERT_TO_EMAIL.split(",")
        if email.strip()
    ]

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": ALERT_FROM_EMAIL,
                "to": recipients,
                "subject": subject,
                "html": html_body,
            },
            timeout=10,
        )

        if response.status_code == 200:
            return True
        else:
            st.warning(
                f"⚠️ Email failed — Resend returned "
                f"HTTP {response.status_code}: {response.text}"
            )
            return False

    except requests.RequestException as e:
        st.warning(f"⚠️ Email failed — network error: {e}")
        return False


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

PRODUCT_URL = "https://carryaura.com/this-page-does-not-exist-99999"


# ==========================================
# Groq API
# ==========================================

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY is not configured.")
    st.stop()

client = Groq(api_key=api_key)


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
            headers={"User-Agent": "CarryAura-AI-Monitor/1.0"}
        )

        status_code = response.status_code

        # ----------------------------------
        # Display website status
        # ----------------------------------

        st.subheader("🌐 Website Status")

        if 200 <= status_code < 400:
            st.success(f"✅ Website is healthy — HTTP {status_code}")

        else:
            st.error(f"❌ Website returned HTTP {status_code}")

            subject = f"🚨 CarryAura Alert: HTTP {status_code}"
            body = f"""
                <h2>🚨 Website Issue Detected</h2>
                <p><strong>URL:</strong> {PRODUCT_URL}</p>
                <p><strong>HTTP Status:</strong> {status_code}</p>
                <p><strong>Meaning:</strong> The website is NOT returning a healthy response.</p>
                <p>Please investigate as soon as possible.</p>
                <hr/>
                <p style="color:#888;font-size:12px;">CarryAura Monitor</p>
            """

            if send_email_alert(subject, body):
                st.info(f"📧 Alert email sent to {ALERT_TO_EMAIL}")
            else:
                st.warning("⚠️ Could not send alert email.")

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
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                include_reasoning=False
            )

        # ----------------------------------
        # Display AI result
        # ----------------------------------

        st.subheader("🤖 AI Analysis")
        st.write(result.choices[0].message.content)

    # ======================================
    # Error Handling
    # ======================================

    except requests.RequestException as e:
        st.error(f"❌ Website check failed: {e}")

        subject = "🚨 CarryAura Alert: Website unreachable"
        body = f"""
            <h2>🚨 Website Unreachable</h2>
            <p><strong>URL:</strong> {PRODUCT_URL}</p>
            <p><strong>Error:</strong> {e}</p>
            <p>The site could not be reached — possible downtime, DNS, or SSL issue.</p>
            <hr/>
            <p style="color:#888;font-size:12px;">CarryAura Monitor</p>
        """
        if send_email_alert(subject, body):
            st.info(f"📧 Alert email sent to {ALERT_TO_EMAIL}")

    except Exception as e:
        st.error(f"❌ Groq/API Error: {e}")
