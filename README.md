# Multi-Agent RAG System

## Project Summary (for Presentation)

### What is this project?
This is an AI-powered document assistant that lets you upload any document (PDF, image, CSV, text) and have a conversation with it — similar to ChatGPT but working on **your own private documents**, running **completely locally** with no internet or paid API required.

### Problem it solves
Students and professionals often have large documents (syllabi, reports, manuals) and need to quickly find specific information. Reading through everything manually is slow. This system lets you just ask a question in plain English and get an accurate answer directly from the document.

### How it works (Simple explanation)
When you ask a question, a team of AI agents work together:
1. **Router Agent** — reads your question and decides the best way to answer it (use your document, search the web, or just chat)
2. **RAG Agent** — searches your uploaded document using an advanced technique called **RAG Fusion** — it generates multiple versions of your question, retrieves the most relevant chunks, and reranks them for accuracy
3. **Web Agent** — if the question needs live information, it searches DuckDuckGo
4. **Synthesizer Agent** — combines all retrieved information and streams the final answer to you in real time
5. **Analysis Agent** — when you upload a document, it automatically generates a full summary, key insights, and a downloadable PDF report

### Key Technologies Used
| Technology | Purpose |
|---|---|
| Ollama + Llama 3 (8B) | Local LLM (runs on your machine, free) |
| ChromaDB | Vector database to store and search document chunks |
| SentenceTransformer | Converts text to embeddings for semantic search |
| RAG Fusion + RRF | Advanced retrieval — generates multiple queries and reranks results |
| DuckDuckGo Search | Live web search when needed |
| Streamlit | Web UI with chat interface |
| PyPDF + Tesseract | PDF parsing and image OCR |
| FPDF2 | PDF report generation |

### What makes it different from a simple chatbot?
- It **knows when to use your document vs. the web vs. just answering** — a simple chatbot always uses the same approach
- **RAG Fusion** retrieves more accurate results than basic search by using multiple query variants and reranking
- **Fully local** — your documents never leave your machine
- **Persistent chat history** — conversations are saved across sessions like ChatGPT
- **Auto-analysis** — every uploaded document gets automatically summarised with key insights

### Real-world use cases
- Ask questions about college syllabi, notes, or textbooks
- Analyse research papers or reports
- Extract information from CSV data files
- Chat with scanned documents (via OCR)

---

A multi-agent document intelligence system built with RAG Fusion, local LLM (Ollama), and a Streamlit UI. Upload documents and chat with them — agents automatically decide whether to retrieve from your docs, search the web, or answer directly.

## Architecture

```
User Query
    ↓
Router Agent  →  rag / web / both / chat
    ↓
RAG Agent (RAG Fusion + ChromaDB)  +  Web Agent (DuckDuckGo)
    ↓
Synthesizer Agent  →  Streamed Answer
```

- **Router** — decides which agents to call based on the query
- **RAG Agent** — generates query variants, retrieves chunks via RAG Fusion (RRF reranking)
- **Web Agent** — fetches live results from DuckDuckGo
- **Synthesizer** — streams the final answer from context
- **Analysis Agent** — auto-analyses uploaded documents and generates PDF reports

## Features

- Upload PDF, PNG, JPG, TXT, MD, CSV files
- OCR support for images (via Tesseract)
- Chat history saved across sessions (like ChatGPT)
- PDF report generation for each uploaded document
- Fully local — no API keys needed (runs on Ollama)

## Prerequisites

### 0. Python 3.10+
Make sure you have Python 3.10 or higher installed. Check with:
```bash
python3 --version
```

### 1. Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Ollama (local LLM — required)
Download and install from [ollama.com](https://ollama.com), then:
```bash
ollama pull llama3
```

### 3. Tesseract (for image OCR — optional)
- **Mac:** `brew install tesseract`
- **Windows:** Download installer from [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux:** `sudo apt install tesseract-ocr`

## Running

**Terminal 1 — start Ollama:**
```bash
ollama serve
```

**Terminal 2 — start the app:**
```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

## Project Structure

```
multi-doc-rag/
├── app.py                  # Streamlit UI
├── agents/
│   ├── base.py             # Color codes + base Agent class
│   ├── router.py           # RouterAgent
│   ├── rag.py              # RAGAgent (RAG Fusion)
│   ├── web.py              # WebAgent (DuckDuckGo)
│   ├── synthesizer.py      # Synthesizer (streaming)
│   └── analysis.py         # AnalysisAgent
├── core/
│   ├── client.py           # Ollama LLM client
│   ├── vectorstore.py      # ChromaDB + SentenceTransformer
│   ├── loader.py           # File loaders (PDF, image, CSV, TXT)
│   ├── report.py           # PDF report generation
│   └── storage.py          # Chat + session persistence
├── .streamlit/
│   └── config.toml         # Light theme config
└── requirements.txt
```

## Notes

- The `data/` folder (ChromaDB, chats, reports) is gitignored — everyone starts fresh
- No API keys required — everything runs locally via Ollama
- Default model: `llama3` (8B; swap to `llama3.2` for a faster, lighter model) (can be changed in `core/client.py`)
