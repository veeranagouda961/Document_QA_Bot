# Document QA Bot (RAG Assistant) 🤖📄

A smart Document Question & Answering assistant powered by **Azure AI Search** and **Azure OpenAI** (Retrieval-Augmented Generation / RAG).

---

## ✨ Features

- **Strict RAG Architecture**: Answers questions strictly based on the provided document context, preventing hallucinations.
- **Azure AI Search Integration**: Fast and semantic document search retrieval.
- **Azure OpenAI Integration**: Natural, accurate answers with source attribution.
- **Interactive Web Interface**: Clean web UI built with HTML/CSS/JS and Flask backend.
- **Source Highlighting**: Cites source documents and page references.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask
- **Search & Retrieval**: Azure AI Search (`azure-search-documents`)
- **LLM**: Azure OpenAI (`openai`)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/veeranagouda961/Document_QA_Bot.git
cd Document_QA_Bot
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (refer to `.env.example`):
```env
# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://<your-search-service-name>.search.windows.net
AZURE_SEARCH_API_KEY=<your-search-api-key>
AZURE_SEARCH_INDEX_NAME=<your-search-index-name>

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://<your-openai-service-name>.openai.azure.com/openai/deployments/<deployment-name>
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment-name>
AZURE_OPENAI_API_KEY=<your-azure-openai-api-key>
```

### 5. Run the Application
```bash
python main.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📂 Project Structure

```
Document_QA_Bot/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── main.py
└── static/
    ├── index.html
    ├── style.css
    └── app.js
```
