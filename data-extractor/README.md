# Local RAG Chat Application: Enterprise Getting Started Guide

Welcome to the **Local RAG (Retrieval-Augmented Generation) Chat Application**. This project provides a robust, private, and customizable chatbot interface that allows you and your teams to securely chat with local business documents (PDFs, Excel files, CSVs, Text files) directly on your own machine. 

This guide serves as the official getting started documentation for all organization members.

---

## 🎯 What it Does

This application acts as a private assistant for your files. By simply dragging and dropping documents into a designated folder, the application:
1. Immediately scans and parses the text using advanced document processors.
2. Converts the information into "vectors" (mathematical representations of text) stored inside a local database.
3. Allows you to ask natural language questions in a chat interface.
4. Retrieves relevant snippets from your documents and uses a Large Language Model (LLM) to synthesize an accurate, cited answer.

---

## 🛠️ Architecture & Tools

This application is built using a modern, scalable AI stack:

- **Frontend/UI**: [Streamlit](https://streamlit.io/) provides the responsive, chat-based web interface.
- **Orchestration**: [LangChain](https://www.langchain.com/) orchestrates the flow between the user prompt, the database, and the LLM.
- **LLM Provider**: Configurable support for powerful cloud LLMs (defaulting to Google Gemini `gemini-2.5-flash`, with support for OpenAI models).
- **Core Embeddings**: Local HuggingFace Sentence Transformers (`all-MiniLM-L6-v2`) handles the vectorization of text *locally* without sending your entire raw documents to the cloud.
- **Vector Database**: [ChromaDB](https://www.trychroma.com/) stores the document embeddings locally.
- **Document Processing**: `unstructured` and `pypdf` handle enterprise-grade extraction from messy file formats (PDFs, spreadsheets).
- **Live File Watcher**: `watchdog` runs in the background. It continuously monitors your data folder to dynamically re-index files the moment they are added, modified, or deleted without requiring an app restart.

---

## 🏗️ Project Structure

```text
data-extractor/
│
├── .env.example          # Template for environment variables
├── .gitignore            # Git exclusions (protects your DB and API keys)
├── README.md             # This getting started guide
├── requirements.txt      # Python dependencies
├── run_app.bat           # Windows startup script
├── run_app.sh            # MacOS/Linux startup script
│
├── app/                  # Application Source Code
│   ├── main.py           # Streamlit UI Entrypoint
│   ├── settings.py       # Configuration and Environment Management
│   ├── watcher.py        # Background File Watcher (Watchdog)
│   └── core/             # AI & Backend Logic
│       ├── database.py   # ChromaDB integration
│       ├── ingestion.py  # Unstructured/PyPDF document chunking
│       └── rag.py        # LangChain Retrieval QA Pipeline
│
├── data/                 # [YOUR FILES GO HERE] The folder monitored by the app
└── chroma_db/            # [AUTO-GENERATED] The local vector database
```

---

## 🚀 Local Setup & Installation

### Prerequisites

Ensure you have the following installed on your machine before beginning:
- **Python 3.9** (Currently recommended for maximum compatibility with all ML dependencies).
- **Git**

### Step 1: Clone the Repository

Clone this project repository to your local machine using your preferred git client or terminal.

### Step 2: Configure Environment Variables & Security

> ⚠️ **CRITICAL SECURITY NOTICE:** You must **NEVER** commit your API keys, `.env` file, or personal databases directly to the Git repository. The `.gitignore` file is pre-configured to prevent this. 

You need to provide your LLM API keys locally to allow the app to generate intelligent responses. 

1. In the root of the project, make a copy of the `.env.example` file and name it `.env`:
   *(On Mac/Linux terminal)*
   ```bash
   cp .env.example .env
   ```
2. Open the newly created `.env` file using any text editor.
3. Uncomment the API key line for your preferred provider and add your personal key:
    ```env
    # LLM Provider Options: gemini, openai
    LLM_PROVIDER=gemini

    # Model Options: gemini-2.5-flash, gpt-4o, gpt-3.5-turbo
    LLM_MODEL=gemini-2.5-flash

    # Add your key here:
    GOOGLE_API_KEY=your_actual_api_key_here
    ```
4. Save the file. Because of the `.gitignore` policy, this file will safely stay on your local machine.

### Step 3: Run the Application

We have provided automated "One-Click" startup scripts that will securely create an isolated Python virtual environment (`venv`), install all required dependencies from `requirements.txt`, and launch the web interface.

**🍎 On macOS / Linux:**
Open your terminal, navigate to the project directory, and run:
```bash
chmod +x run_app.sh   # Grants execution permissions (only needed once)
./run_app.sh          # Starts the app 
```

**🪟 On Windows:**
Open Command Prompt or PowerShell, navigate to the project directory, and double-click or run:
```cmd
run_app.bat
```

### Step 4: Add Documents & Chat!

1. After the setup script finishes, a new tab will automatically open in your default web browser pointing to `http://localhost:8501`.
2. Look at your local project folder and find the `data/` directory (create it in the root if it isn't there).
3. Drop any relevant files (PDFs, TXT, CSV, XLSX) into the `data/` folder.
4. The background File Watcher will immediately detect the new files, chunk them, and save them to your local vector database.
5. Go to your browser and ask the AI a question regarding the files you just added!

---

## 📝 Usage Notes & Troubleshooting

- **Changing Providers**: To switch from Google Gemini to OpenAI, open your `.env` file, change `LLM_PROVIDER` to `openai`, update the `LLM_MODEL` name, and ensure `OPENAI_API_KEY` is set. Restart the app.
- **Python Version Issues on Mac**: In testing, Python 3.12 has known compatibility issues with building machine learning packages like `llvmlite`/`numba` from source. If you experience build failures during `./run_app.sh`, explicitly install and use Python 3.9 or 3.10.
- **Clearing the Database**: If you ever want to completely reset the AI's memory, simply delete the `chroma_db/` folder while the app is closed. It will automatically be rebuilt the next time you start the app.
