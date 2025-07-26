import streamlit as st
import pandas as pd
import time
import subprocess
import sys
import os

# Add project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from bot.database import Database

# ---------- Helper Functions ----------
def load_messages(db, limit=50):
    db.cursor.execute("""
        SELECT messages.thread_id,
               messages.subject,
               messages.body,
               messages.is_from_bot,
               messages.timestamp,
               senders.summary AS sender_summary
        FROM messages
        LEFT JOIN senders ON messages.sender_id = senders.id
        ORDER BY messages.timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = db.cursor.fetchall()
    cols = [desc[0] for desc in db.cursor.description]
    return pd.DataFrame(rows, columns=cols)

def load_senders(db):
    db.cursor.execute("SELECT id, summary FROM senders ORDER BY id")
    rows = db.cursor.fetchall()
    return pd.DataFrame(rows, columns=["sender_id", "summary"])

def load_thread_messages(db, thread_id):
    db.cursor.execute("""
        SELECT messages.sender_id, messages.body, messages.is_from_bot, messages.timestamp
        FROM messages
        WHERE thread_id = ?
        ORDER BY timestamp ASC
    """, (thread_id,))
    rows = db.cursor.fetchall()
    return pd.DataFrame(rows, columns=["sender_id", "body", "is_from_bot", "timestamp"])

# ---------- Streamlit App ----------
st.set_page_config(page_title="AutoTA Dashboard", layout="wide")
st.title("📬 AutoTA Gmail Bot Dashboard")

# Initialize database
db = Database()

tab1, tab2, tab3 = st.tabs(["Messages", "Senders", "Bot Control"])

# ---- Tab 1: Messages & Thread Viewer ----
with tab1:
    st.header("Recent Messages")
    messages_df = load_messages(db)
    if not messages_df.empty:
        st.dataframe(messages_df, use_container_width=True)

        thread_ids = messages_df["thread_id"].unique().tolist()
        thread_id = st.selectbox("Select a thread to view conversation", thread_ids)
        if thread_id:
            st.subheader(f"Thread: {thread_id}")
            thread_df = load_thread_messages(db, thread_id)
            for _, row in thread_df.iterrows():
                role = "🤖 Bot" if row["is_from_bot"] else "👤 User"
                st.markdown(
                    f"**{role} ({row['sender_id']})**  "
                    f"*({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row['timestamp']))})*"
                )
                st.markdown(row["body"])
                st.markdown("---")
    else:
        st.info("No messages found in database.")

# ---- Tab 2: Sender Summaries ----
with tab2:
    st.header("Sender Summaries")
    senders_df = load_senders(db)
    if not senders_df.empty:
        st.dataframe(senders_df, use_container_width=True)

        st.subheader("Edit Sender Summary")
        sender_to_edit = st.selectbox("Select sender", senders_df['sender_id'])
        if sender_to_edit:
            current_summary = senders_df.loc[
                senders_df['sender_id'] == sender_to_edit, "summary"
            ].values[0]
            new_summary = st.text_area("New summary", current_summary, height=150)
            if st.button("Update Summary"):
                db.update_sender_summary(sender_to_edit, new_summary)
                st.success("Summary updated!")
                time.sleep(1)
                st.experimental_rerun()
    else:
        st.info("No senders found in database.")

# ---- Tab 3: Bot Control ----
with tab3:
    st.header("Manual Bot Run")
    st.write("Click the button to run the bot immediately.")
    if st.button("Run Bot Now"):
        with st.spinner("Running bot..."):
            result = subprocess.run(
                ["python", "-m", "bot.main"],
                capture_output=True,
                text=True
            )
            st.subheader("Bot Output")
            st.text(result.stdout)
            if result.stderr:
                st.error(result.stderr)

# Clean up
db.close()