import streamlit as st
import pandas as pd
import time
import subprocess
import sys
import os
from helpers import latex_to_markdown

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

tab1, tab2, tab3, tab4 = st.tabs(["Messages", "Senders", "Bot Control", "Documents"])

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
                st.rerun()
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

with tab4:
    st.header("📄 Document Management")

    uploaded_files = st.file_uploader(
        "Upload one or more text/LaTeX files",
        type=["txt", "tex"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Save All Documents"):
            for uploaded_file in uploaded_files:
                try:
                    content = uploaded_file.read().decode("utf-8")
                    filename = uploaded_file.name

                    # --- Check for LaTeX files ---
                    if filename.endswith(".tex"):
                        st.info(f"Converting {filename} from LaTeX to Markdown...")
                        content = latex_to_markdown(content)
                        filename = filename.replace(".tex", ".md")  # store as markdown
                        st.success(f"{filename} saved (converted from LaTeX)!")
                    else:
                        st.success(f"{filename} saved successfully!")

                    db.add_document(filename, content)
                except Exception as e:
                    st.error(f"Error saving {uploaded_file.name}: {e}")
            st.rerun()

    # List existing documents
    docs = db.list_documents()
    if docs:
        st.subheader("Existing Documents")
        for doc_id, filename, size, created_at in docs:
            with st.expander(f"{filename} ({size} chars) - {created_at}"):
                new_name = st.text_input(f"Rename {filename}", filename, key=f"rename_{doc_id}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Rename", key=f"btn_rename_{doc_id}"):
                        db.update_document_name(doc_id, new_name)
                        st.success("Filename updated!")
                        st.rerun()
                with col2:
                    if st.button("Delete", key=f"btn_delete_{doc_id}"):
                        db.delete_document(doc_id)
                        st.warning(f"{filename} deleted!")
                        st.rerun()

                if st.checkbox("Show content", key=f"show_{doc_id}"):
                    st.text(db.get_document_content(doc_id))
    else:
        st.info("No documents found.")

# Clean up
db.close()