import os
import html
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st

from core.loader import load_file
from core.vectorstore import VectorStore
from core.report import generate_pdf
from core.storage import (save_state, load_state, clear_state,
                           save_chat, load_chat, list_chats, delete_chat, new_chat_id)
from agents import RouterAgent, RAGAgent, WebAgent, Synthesizer, AnalysisAgent

load_dotenv()

st.set_page_config(page_title="Multi-Agent RAG", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }

/* ── Collapse the hidden header space ───────── */
header[data-testid="stHeader"] {
    height: 0 !important;
    min-height: 0 !important;
    visibility: hidden;
}

/* ── Lock sidebar open ───────────────────── */
[data-testid="collapsedControl"] { display: none !important; }
button[data-testid="baseButton-header"] { display: none !important; }
section[data-testid="stSidebar"] {
    min-width: 260px !important;
    max-width: 260px !important;
    transform: none !important;
    visibility: visible !important;
    top: 0 !important;
}

/* ── Remove top gap from main content ───────── */
.main .block-container {
    padding-top: 0.5rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    padding-bottom: 7rem !important;
    max-width: 100% !important;
}

/* ── Fix tab bar to top of page ─────────────── */
.stTabs [data-baseweb="tab-list"] {
    position: fixed !important;
    top: 0;
    left: 260px;
    right: 0;
    z-index: 200;
    background: #ffffff !important;
    border-bottom: 2px solid #e2e8f0 !important;
    padding: 0 1rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* ── Push tab content below fixed navbar ────── */
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 3rem !important;
}

/* ── Pin chat input to bottom ────────────── */
.stChatInput {
    position: fixed;
    bottom: 0;
    left: 260px;
    right: 0;
    z-index: 998;
    background: #f4f6f9;
    padding: 0.6rem 1.5rem 0.8rem 1.5rem;
    border-top: 1px solid #e2e8f0;
}
.stChatInput > div {
    max-width: 100% !important;
    width: 100% !important;
}

/* ── Sidebar ─────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0;
    padding-top: 1.5rem;
}
section[data-testid="stSidebar"] .block-container {
    padding: 0 1rem;
}

/* ── Tabs ────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    border-radius: 10px 10px 0 0;
    border-bottom: 2px solid #e2e8f0;
    gap: 0;
    padding: 0 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 500;
    font-size: 0.9rem;
    padding: 0.7rem 1.2rem;
    color: #64748b;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
}
.stTabs [aria-selected="true"] {
    color: #c0392b !important;
    border-bottom: 3px solid #c0392b !important;
    background: transparent !important;
}

/* ── Buttons ─────────────────────────────── */
div.stButton > button[kind="primary"] {
    background: #c0392b !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    padding: 0.6rem 1rem !important;
    width: 100%;
    transition: background 0.2s;
}
div.stButton > button[kind="primary"]:hover {
    background: #a93226 !important;
}
div.stButton > button[kind="secondary"] {
    background: white !important;
    color: #374151 !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: #c0392b !important;
    color: #c0392b !important;
}

/* ── Download button ─────────────────────── */
div.stDownloadButton > button {
    background: #1d4ed8 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-size: 0.82rem !important;
    padding: 0.35rem 0.8rem !important;
    font-weight: 500 !important;
}

/* ── Metric cards ────────────────────────── */
div[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* ── File uploader ───────────────────────── */
section[data-testid="stFileUploadDropzone"] {
    background: #ffffff;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 10px;
}
section[data-testid="stFileUploadDropzone"]:hover {
    border-color: #c0392b !important;
}

/* ── Success / info / error boxes ───────── */
div[data-testid="stAlert"] {
    border-radius: 8px;
}

/* ── Expander ────────────────────────────── */
div[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ── Chat messages ───────────────────────── */
div[data-testid="stChatMessage"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.8rem;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── session state ──────────────────────────────────────────────────────────────

if "initialized" not in st.session_state:
    sources, reports = load_state()
    st.session_state.vs          = VectorStore()
    st.session_state.sources     = sources
    st.session_state.reports     = reports
    st.session_state.chat_id     = new_chat_id()
    st.session_state.messages    = []
    st.session_state.initialized = True

# ── agents ─────────────────────────────────────────────────────────────────────

router      = RouterAgent()
rag_agent   = RAGAgent()
web_agent   = WebAgent()
synthesizer = Synthesizer()
analyser    = AnalysisAgent()

# ── sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    # ── new chat ───────────────────────────────
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.chat_id  = new_chat_id()
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # ── chat history ───────────────────────────
    st.markdown("<p style='font-size:0.85rem;font-weight:600;color:#374151;margin-bottom:0.4rem'>Chat History</p>", unsafe_allow_html=True)
    past_chats = list_chats()
    if not past_chats:
        st.caption("No previous chats yet.")
    for chat in past_chats:
        is_active = chat["id"] == st.session_state.chat_id
        col1, col2 = st.columns([5, 1])
        label = ("▶ " if is_active else "") + chat["title"][:30]
        if col1.button(label, key=f"chat_{chat['id']}", use_container_width=True):
            st.session_state.chat_id  = chat["id"]
            st.session_state.messages = load_chat(chat["id"])
            st.rerun()
        if col2.button("✕", key=f"del_{chat['id']}"):
            delete_chat(chat["id"])
            if chat["id"] == st.session_state.chat_id:
                st.session_state.chat_id  = new_chat_id()
                st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    # ── system status ──────────────────────────
    try:
        from core.client import llm, MODEL
        llm.models.list()
        st.success("LLM connected", icon="✅")
    except Exception:
        st.error("LLM not reachable")

    st.markdown(
        f"<div style='background:#f1f5f9;border-radius:8px;padding:0.6rem 0.9rem;"
        f"margin:0.5rem 0;font-size:0.88rem;color:#374151;'>"
        f"<b>Knowledge base:</b> {st.session_state.vs.count()} chunks</div>",
        unsafe_allow_html=True,
    )

    if st.session_state.sources:
        st.markdown("<p style='font-size:0.85rem;font-weight:600;color:#374151;margin-bottom:0.3rem'>Processed files</p>", unsafe_allow_html=True)
        for src in st.session_state.sources:
            ext = src["name"].rsplit(".", 1)[-1].lower()
            icon = {"pdf": "📄", "csv": "📊", "txt": "📝", "md": "📝"}.get(ext, "🖼️")
            st.markdown(
                f"<div style='font-size:0.83rem;padding:0.25rem 0;color:#4b5563'>{icon} {src['name']}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    if st.button("🗑️ Clear knowledge base", use_container_width=True):
        st.session_state.vs.clear()
        st.session_state.sources.clear()
        st.session_state.reports.clear()
        clear_state()
        st.rerun()


# ── tab persistence via URL query param ────────────────────────────────────────

import streamlit.components.v1 as components
components.html("""
<script>
(function() {
    const params = new URLSearchParams(window.parent.location.search);
    const activeTab = parseInt(params.get('tab') || '0');

    function init() {
        const tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
        if (!tabs.length) { setTimeout(init, 80); return; }

        if (tabs[activeTab]) tabs[activeTab].click();

        tabs.forEach(function(tab, i) {
            tab.addEventListener('click', function() {
                const url = new URL(window.parent.location.href);
                url.searchParams.set('tab', i);
                window.parent.history.replaceState({}, '', url.toString());
            });
        });
    }

    setTimeout(init, 250);
})();
</script>
""", height=0)

# ── tabs ───────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Process", "📋 Results", "💬 Chat with Docs", "📁 Reports"])

# ── tab 1: upload ──────────────────────────────────────────────────────────────

with tab1:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f2460 0%,#1e3a8a 100%);
                color:white;padding:2rem 2.5rem;border-radius:12px;margin-bottom:1.5rem;">
        <div style="font-size:1.75rem;font-weight:700;margin-bottom:0.4rem;">
            🔍 Multi-Agent Enterprise Intelligence System
        </div>
        <div style="color:#93c5fd;font-size:0.97rem;">
            Upload documents → AI agents analyse, summarise, and answer your questions
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Upload a document")
    st.caption("Supported formats: **PDF** · **PNG / JPG / JPEG** (OCR) · **TXT / MD / CSV**")

    uploaded = st.file_uploader(
        "",
        type=["pdf", "png", "jpg", "jpeg", "txt", "md", "csv"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded:
        st.markdown("")
        for f in uploaded:
            col1, col2, col3 = st.columns(3)
            col1.metric("File", f.name)
            col2.metric("Size", f"{f.size / 1024:.1f} KB")
            col3.metric("Type", f.name.rsplit(".", 1)[-1].upper())

        st.markdown("")
        if st.button("🚀 Run all agents", type="primary", use_container_width=True):
            for f in uploaded:
                if any(s["name"] == f.name for s in st.session_state.sources):
                    st.info(f"{f.name} already processed.")
                    continue

                file_bytes = f.read()
                st.markdown(f"**Processing {f.name}...**")
                progress  = st.progress(0)
                status_ph = st.empty()

                try:
                    status_ph.markdown("🔍 &nbsp;Loading document...")
                    progress.progress(10)
                    chunks = load_file(file_bytes, f.name)

                    status_ph.markdown("⚙️ &nbsp;Building vector index...")
                    progress.progress(35)
                    st.session_state.vs.add(chunks, f.name)

                    status_ph.markdown("🧠 &nbsp;Running analysis agent...")
                    progress.progress(55)
                    raw_text = " ".join(chunks[:25])
                    analysis = analyser.run(raw_text, f.name)

                    status_ph.markdown("📄 &nbsp;Generating PDF report...")
                    progress.progress(80)
                    stats = {
                        "File name":            f.name,
                        "Source type":          f.name.rsplit(".", 1)[-1].upper(),
                        "Characters extracted": len(raw_text),
                        "Words extracted":      len(raw_text.split()),
                        "Chunks indexed":       len(chunks),
                    }
                    pdf_bytes   = generate_pdf(f.name, {"summary": analysis, "stats": stats})
                    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
                    report_name = f"{f.name.rsplit('.', 1)[0]}_report_{timestamp}.pdf"

                    st.session_state.reports.append({"filename": report_name, "bytes": pdf_bytes})
                    st.session_state.sources.append({"name": f.name, "analysis": analysis, "stats": stats})
                    save_state(st.session_state.sources, st.session_state.reports)

                    progress.progress(100)
                    status_ph.empty()
                    st.success(f"✅ Done — {len(chunks)} chunks indexed from **{f.name}**")

                except Exception as e:
                    # roll back partially indexed chunks so a retry doesn't duplicate them
                    st.session_state.vs.remove(f.name)
                    progress.empty()
                    status_ph.empty()
                    st.error(f"Error: {e}")

# ── tab 2: results ─────────────────────────────────────────────────────────────

with tab2:
    st.markdown("### 📋 Results")
    if not st.session_state.sources:
        st.info("Upload and process a document first.")
    else:
        for src in st.session_state.sources:
            with st.expander(f"📄 {src['name']}", expanded=True):
                st.markdown("**Document Statistics**")
                cols = st.columns(len(src["stats"]))
                for col, (k, v) in zip(cols, src["stats"].items()):
                    col.metric(k, v)
                st.markdown("---")
                st.markdown("### Summary & Insights")
                st.markdown(src["analysis"])

# ── tab 3: chat ────────────────────────────────────────────────────────────────

with tab3:
    st.markdown("### 💬 Chat with your documents")
    count = st.session_state.vs.count()
    if count > 0:
        st.caption(f"Knowledge base contains **{count} chunks** from your documents.")
    else:
        st.info("Upload and process documents first to enable RAG. Web search is always available.")

    def render_bubble(role, content):
        if role == "user":
            st.markdown(
                f"<div style='display:flex;justify-content:flex-end;margin:0.4rem 0;'>"
                f"<div style='background:#c0392b;color:white;padding:0.65rem 1rem;"
                f"border-radius:18px 18px 4px 18px;max-width:72%;"
                f"font-size:0.95rem;line-height:1.5;word-wrap:break-word;'>"
                f"{html.escape(content)}</div></div>",
                unsafe_allow_html=True
            )
        else:
            # each st.markdown is its own element, so raw <div> wrappers can't enclose the answer —
            # use a bordered container in a left column instead
            col, _ = st.columns([3, 1])
            with col.container(border=True):
                st.markdown(content)

    for msg in st.session_state.messages:
        render_bubble(msg["role"], msg["content"])

    query = st.chat_input("Ask a question about your documents or anything...")

    if query:
        history = list(st.session_state.messages)
        st.session_state.messages.append({"role": "user", "content": query})
        render_bubble("user", query)

        with st.status("Running agents...", expanded=True) as status:
            has_docs = st.session_state.vs.count() > 0
            standalone = rag_agent.condense(query, history)
            if standalone != query:
                st.write(f"🧩 **Follow-up rewritten** → _{standalone}_")
            decision = router.run(standalone, has_docs)
            st.write(f"🔀 **Router** → `{decision}`")

            if decision == "chat":
                from core.client import llm, MODEL
                def _chat_stream():
                    for chunk in llm.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant. Reply naturally and concisely."}
                        ] + [{"role": m["role"], "content": m["content"]} for m in history[-6:]] + [
                            {"role": "user", "content": query}
                        ],
                        stream=True
                    ):
                        delta = chunk.choices[0].delta.content
                        if delta:
                            yield delta
            else:
                context = []
                if decision in ("rag", "both"):
                    if has_docs:
                        docs = rag_agent.run(standalone, st.session_state.vs)
                        context.extend(docs)
                        st.write(f"📚 **RAG Agent** → retrieved {len(docs)} chunks via RAG Fusion")
                    else:
                        st.write("📚 **RAG Agent** → skipped (no documents loaded)")

                if decision in ("web", "both"):
                    snippets = web_agent.run(standalone)
                    context.extend(snippets)
                    st.write(f"🌐 **Web Agent** → fetched {len(snippets)} results")

                st.write("✍️ **Synthesizer** → streaming...")
                def _chat_stream():
                    return synthesizer.stream(standalone, context, history)

            status.update(label="✅ Done", state="complete")

        result = st.write_stream(_chat_stream())

        st.session_state.messages.append({"role": "assistant", "content": result})
        title = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "Chat")[:50]
        save_chat(st.session_state.chat_id, title, st.session_state.messages)
        st.rerun()

# ── tab 4: reports ─────────────────────────────────────────────────────────────

with tab4:
    st.markdown("### 📁 Generated Reports")
    if not st.session_state.reports:
        st.info("No reports yet. Process documents to generate them.")
    else:
        st.markdown(f"Found **{len(st.session_state.reports)}** report(s):")
        st.markdown("---")
        for r in st.session_state.reports:
            col1, col2 = st.columns([5, 1])
            col1.markdown(
                f"<div style='padding:0.6rem 0;font-size:0.88rem;color:#374151'>📄 <code>{r['filename']}</code></div>",
                unsafe_allow_html=True,
            )
            col2.download_button(
                "⬇️ Download",
                data=r["bytes"],
                file_name=r["filename"],
                mime="application/pdf",
                key=r["filename"],
            )
