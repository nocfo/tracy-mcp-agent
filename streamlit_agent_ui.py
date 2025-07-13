import streamlit as st
from jwt_utils import generate_token
import requests

BOT_AVATAR = "🤖"
USER_AVATAR = "👤"

st.set_page_config(page_title="AI Agent Demo", page_icon="🤖")
st.title("🧑‍💼📊 Chat with your CFO")

# ------------------------
# Login Panel
# ------------------------
st.sidebar.header("User Login Simulation")
username = st.sidebar.text_input("Username", value="alice")
company_id = st.sidebar.text_input("Company ID", value="RetailGiant")

if st.sidebar.button("Login & Generate Token"):
    if username and company_id:
        token = generate_token(user_id=username, company_id=company_id)
        st.sidebar.success("✅ Login successful")
        st.session_state["token"] = token
    else:
        st.sidebar.error("Please fill in both username and company ID")

# ------------------------
# Login Required Check
# ------------------------
if "token" not in st.session_state:
    st.warning("Please login and generate a token in the sidebar first.")
    st.stop()

token = st.session_state["token"]

# ------------------------
# Chat History State
# ------------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ------------------------
# Chat Area
# ------------------------
st.markdown("### 💬 Ask Me Anything! ")

question = st.text_input("Your question", key="input_field")

if st.button("Send"):
    if question.strip() == "":
        st.warning("Please enter a question.")
    else:
        # Append user message to history
        st.session_state.chat_history.append((USER_AVATAR, question))

        # Send to AI Agent API
        def send_message(q, token):
            API_URL = "http://localhost:8001/ask"
            headers = {"Content-Type": "application/json"}
            payload = {"question": q, "token": token}
            try:
                resp = requests.post(API_URL, json=payload, headers=headers)
                if resp.status_code == 200:
                    return resp.json().get("answer", "⚠️ Unable to retrieve response.")
                else:
                    return f"❌ Request failed. Status code: {resp.status_code}"
            except Exception as e:
                return f"❌ Request error: {str(e)}"

        answer = send_message(question, token)
        st.session_state.chat_history.append((BOT_AVATAR, answer))

# ------------------------
# Chat History Display (Top to Bottom)
# ------------------------
for avatar, message in st.session_state.chat_history:
    if avatar == USER_AVATAR:
        # User message bubble
        st.markdown(
            f"""
    <div style="text-align: right;">
        <div style="
            display: inline-block;
            background-color: #f0f0f5;
            padding: 12px 16px;
            border-radius: 10px;
            margin: 8px 0;
            max-width: 80%;
            word-wrap: break-word;
        ">
            {message}
        </div>
    </div>
    """,
            unsafe_allow_html=True
        )
    else:
        # AI message bubble
        st.markdown(
            f"""
            <div style="background-color:#e8f4fc; padding:12px; border-radius:8px; margin:8px 0; text-align:left;">
                <b>🤖 AI:</b><br>{message}
            </div>
            """,
            unsafe_allow_html=True
        )
