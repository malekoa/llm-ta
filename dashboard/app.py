import atexit
import streamlit as st
import pandas as pd
import time
import subprocess
import sys
import os
from helpers import latex_to_markdown, chunk_text
from apscheduler.schedulers.background import BackgroundScheduler


# Add project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from bot.database import Database
from bot.embeddings import embed_chunk

# ---------- Helper Functions ----------
def load_messages(db, limit=50):
    db.cursor.execute("""
        SELECT messages.thread_id,
               messages.id AS message_id,
               messages.subject,
               messages.body,
               messages.is_from_bot,
               messages.timestamp,
               senders.summary AS sender_summary,
               votes.vote AS vote
        FROM messages
        LEFT JOIN senders ON messages.sender_id = senders.id
        LEFT JOIN votes ON votes.message_id = messages.id
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

def fetch_embeddings_for_document(db, doc_id):
    chunks = db.list_document_chunks(doc_id)
    for chunk_id, idx, size, content in chunks:
        db.cursor.execute("SELECT embedding FROM document_chunks WHERE id = ?", (chunk_id,))
        if db.cursor.fetchone()[0] is None:  # no embedding yet
            embedding = embed_chunk(content)
            db.update_chunk_embedding(chunk_id, embedding)
    st.success("Embeddings fetched for all chunks!")

def tail(filepath, lines=50):
    """Return the last `lines` of the given file."""
    try:
        with open(filepath, 'r') as f:
            return ''.join(f.readlines()[-lines:])
    except FileNotFoundError:
        return "Log file not found."
    
def verify_user(username, password):
    with Database() as db:
        db.ensure_user_table()
        return db.verify_user(username, password)


# ---------- Simple Auth ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.set_page_config(page_title="TARA Dashboard Login", layout="centered")
    st.title("🔒 TARA Dashboard Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if verify_user(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

# ---------- Streamlit App ----------
st.set_page_config(page_title="TARA Dashboard", layout="wide")
st.title("📬 AutoTA Gmail Bot Dashboard")

# --- Manage DB connection per session ---
if "db" not in st.session_state:
    st.session_state.db = Database()

db = st.session_state.db

# ---- Initialize Scheduler ----
if "scheduler" not in st.session_state:
    st.session_state.scheduler = BackgroundScheduler()
    st.session_state.scheduler.start()
    st.session_state.job = None

# Load saved interval from DB on first run
if "interval_minutes" not in st.session_state:
    db.ensure_settings_table()
    saved_interval = db.get_setting("interval_minutes", "120")
    st.session_state.interval_minutes = int(saved_interval)

def run_bot():
    subprocess.run(["python", "-m", "bot.main"])


# Close DB when Streamlit shuts down
def close_db():
    if "db" in st.session_state:
        try:
            st.session_state.db.close()
        finally:
            del st.session_state.db

atexit.register(close_db)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Messages", "Senders", "Bot Settings", "RAG Documents", "Document Chunks"]
)

# ---- Tab 1: Messages & Thread Viewer ----
with tab1:
    st.header("✉️ Recent Messages")
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
                vote_display = f" (Vote: {row.get('vote', 'none')})" if row["is_from_bot"] else ""
                st.markdown(
                    f"**{role} ({row['sender_id']}){vote_display}**  "
                    f"*({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row['timestamp']))})*"
                )
                st.markdown(row["body"])
                st.markdown("---")
    else:
        st.info("No messages found in database.")

# ---- Tab 2: Sender Summaries ----
with tab2:
    st.header("👤 Sender Summaries")
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
    st.header("⚙️ Bot Settings")

    st.subheader("Feature Toggles")

    sender_limit_enabled = db.get_setting("sender_limit_enabled", "1") == "1"
    auto_response_enabled = db.get_setting("auto_response_enabled", "1") == "1"

    new_sender_limit_enabled = st.checkbox(
        "Enable sender daily limit check", value=sender_limit_enabled
    )

    if st.button("Save Feature Toggles"):
        db.set_setting("sender_limit_enabled", "1" if new_sender_limit_enabled else "0")
        st.success("Feature toggles updated!")

    # Current values
    current_hours = st.session_state.interval_minutes // 60
    current_minutes = st.session_state.interval_minutes % 60

    col1, col2 = st.columns(2)
    with col1:
        hours = st.number_input("Hours", 0, 24, current_hours)
    with col2:
        minutes = st.number_input("Minutes", 0, 59, current_minutes)

    total_minutes = hours * 60 + minutes
    st.caption(f"Selected interval: **{hours}h {minutes}m**")

    if st.button("Save Schedule"):
        st.session_state.interval_minutes = total_minutes
        db.set_setting("interval_minutes", str(total_minutes))

        if st.session_state.job:
            st.session_state.scheduler.remove_job(st.session_state.job.id)

        if total_minutes > 0:
            st.session_state.job = st.session_state.scheduler.add_job(
                run_bot,
                'interval',
                minutes=total_minutes,
                id='bot_job',
                replace_existing=True
            )
            st.success(f"Updated schedule: every {hours}h {minutes}m")
        else:
            st.session_state.job = None
            st.warning("Automatic schedule disabled (0 interval).")

    st.subheader("Daily Sender Limit")
    if "daily_sender_limit" not in st.session_state:
        st.session_state.daily_sender_limit = int(db.get_setting("daily_sender_limit", "10"))

    new_limit = st.number_input(
        "Max responses per sender per day", min_value=1, value=st.session_state.daily_sender_limit
    )
    if st.button("Save Sender Limit"):
        db.set_setting("daily_sender_limit", str(new_limit))
        st.session_state.daily_sender_limit = new_limit
        st.success("Sender limit updated!")

    st.subheader("🏁 Run Bot Manually")
    if st.button("Run Bot Now"):
        log_path = os.path.join(ROOT_DIR, "bot.log")
        prev_size = os.path.getsize(log_path) if os.path.exists(log_path) else 0

        with st.spinner("Running bot..."):
            subprocess.run(["python", "-m", "bot.main"])
            time.sleep(0.5)

        st.subheader("Bot Log (new lines after run)")
        with open(log_path, "r") as f:
            f.seek(prev_size)
            new_lines = f.read()
        st.code(new_lines if new_lines else "(No new log entries)", language="")

    with st.expander("📜 View Latest Logs", expanded=False):
        num_lines = st.slider("Lines to show", 50, 500, 200, step=50)
        log_output = tail(os.path.join(ROOT_DIR, "bot.log"), lines=num_lines)
        st.code(log_output, language="")

with tab4:
    st.header("📄 RAG Documents")

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

                    # Convert LaTeX → Markdown if needed
                    if filename.endswith(".tex"):
                        st.info(f"Converting {filename} from LaTeX to Markdown...")
                        content = latex_to_markdown(content)
                        filename = filename.replace(".tex", ".md")
                        st.success(f"{filename} saved (converted from LaTeX)!")
                    else:
                        st.success(f"{filename} saved successfully!")

                    # Insert document
                    db.add_document(filename, content)

                    # Get new document id
                    doc_id = db.cursor.lastrowid

                    # Chunk document
                    chunks = chunk_text(content, filename=filename)
                    for i, chunk in enumerate(chunks):
                        db.add_chunk(doc_id, i, chunk)
                    st.success(f"Document split into {len(chunks)} chunks.")

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
                col1, col2, col3 = st.columns(3)
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
                with col3:
                    # --- Check if any chunk is missing embedding ---
                    db.cursor.execute(
                        "SELECT COUNT(*) FROM document_chunks WHERE document_id = ? AND embedding IS NULL",
                        (doc_id,)
                    )
                    missing_count = db.cursor.fetchone()[0]
                    if missing_count == 0:
                        st.info("✅ Embeddings already generated")
                    else:
                        if st.button(f"Fetch embeddings ({missing_count} missing)", key=f"embed_{doc_id}"):
                            chunks = db.list_document_chunks(doc_id)
                            progress = st.progress(0)
                            for i, (chunk_id, idx, size, content) in enumerate(chunks):
                                # Only embed chunks without embedding
                                db.cursor.execute(
                                    "SELECT embedding FROM document_chunks WHERE id = ?", (chunk_id,)
                                )
                                if db.cursor.fetchone()[0] is None and content.strip():
                                    embedding = embed_chunk(content)
                                    db.update_chunk_embedding(chunk_id, embedding)

                                # Update progress bar
                                progress.progress((i + 1) / len(chunks))
                            st.success(f"Embeddings generated for {filename}")
                            st.rerun()

                if st.checkbox("Show content", key=f"show_{doc_id}"):
                    st.text(db.get_document_content(doc_id))
    else:
        st.info("No documents found.")

with tab5:
    st.header("🔍 Document Chunks Viewer")

    docs = db.list_documents()
    if docs:
        # Dropdown to select document
        doc_options = {f"{filename} (ID: {doc_id})": doc_id for doc_id, filename, size, created_at in docs}
        selected_doc = st.selectbox("Select a document", list(doc_options.keys()))
        doc_id = doc_options[selected_doc]

        chunks = db.list_document_chunks(doc_id)
        if chunks:
            st.write(f"Found **{len(chunks)} chunks** for this document.")

            # Summary table
            summary_df = pd.DataFrame(
                [{"Chunk Index": idx, "Size (chars)": size} for (_, idx, size, _) in chunks]
            )
            st.dataframe(summary_df, use_container_width=True)

            # Expanders to show chunk content
            for chunk_id, idx, size, content in chunks:
                with st.expander(f"Chunk {idx} ({size} chars)"):
                    st.text(content)
        else:
            st.info("No chunks found for this document.")
    else:
        st.info("No documents found.")