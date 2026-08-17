import sys
import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import OpenAI
from flask import Flask, request, jsonify, send_from_directory
import markdown

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load environment variables from .env file
load_dotenv()

# Azure AI Search details
ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

if not API_KEY or not ENDPOINT or not INDEX_NAME:
    raise ValueError("Missing Azure AI Search environment variables in .env file.")

# Create search client
search_client = SearchClient(
    endpoint=ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(API_KEY)
)

# Azure OpenAI details
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

if not OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT or not DEPLOYMENT_NAME:
    raise ValueError("Missing Azure OpenAI environment variables in .env file.")

openai_client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=OPENAI_API_KEY
)


# System instruction for strict RAG behavior
SYSTEM_INSTRUCTION = """You are a document question-answering assistant.

Answer ONLY using the information provided in the CONTEXT.

Rules:
- Do not use your general knowledge.
- Do not make assumptions.
- Do not invent information.
- Do not hallucinate.
- If the answer is not clearly supported by the CONTEXT, respond exactly:
  'I am not sure about that based on the available documents.'
- If the context contains insufficient information to answer confidently, respond exactly:
  'I am not sure about that based on the available documents.'
- If the documents contain conflicting information, do not choose an answer using general knowledge. Clearly mention that the documents contain conflicting information.
- Keep the answer concise and directly answer the user's question.
- Also make sure to keep it short and simple. Avoid long answers; bullet points are preferred."""


# Search function
def search_documents(query, target_document="BrightPath_Solutions_Company_Policy.md"):
    filter_expr = f"metadata_storage_name eq '{target_document}'" if target_document else None
    results = search_client.search(
        search_text=query,
        filter=filter_expr,
        top=5
    )

    documents = []
    for result in results:
        documents.append({
            "content": result.get("content", ""),
            "metadata_storage_name": result.get("metadata_storage_name", "Unknown"),
            "metadata_storage_path": result.get("metadata_storage_path", "")
        })

    return documents


# Generate answer using Azure OpenAI
def generate_answer(question, documents):
    # Build clean context from retrieved documents
    context_parts = []
    sources = []

    for doc in documents:
        source_name = doc["metadata_storage_name"]
        content = doc["content"]

        if content:
            context_parts.append(f"Source: {source_name}\n\n{content}")
            if source_name not in sources:
                sources.append(source_name)

    context = "\n\n---\n\n".join(context_parts)

    # Build the prompt
    user_message = f"""CONTEXT:

{context}

---

QUESTION: {question}"""

    try:
        response = openai_client.responses.create(
            model=DEPLOYMENT_NAME,
            input=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": user_message}
            ]
        )

        answer = response.output_text
        return answer, sources

    except Exception as e:
        print(f"\nBot: Sorry, something went wrong while generating the answer: {e}")
        return None, []


# ─── Flask Web Server ───────────────────────────────────────

app = Flask(__name__, static_folder="static")


@app.route("/")
def serve_ui():
    """Serve the main chat UI."""
    return send_from_directory("static", "index.html")


@app.route("/api/search", methods=["POST"])
def api_search():
    """API endpoint: accepts { question } and returns { answer, sources }."""
    data = request.get_json(silent=True)

    if not data or not data.get("question", "").strip():
        return jsonify({"error": "Please provide a question."}), 400

    question = data["question"].strip()

    try:
        # Step 1: Search documents
        documents = search_documents(question)

        # Step 2: No results
        if not documents:
            return jsonify({
                "answer": "<p>I am not sure about that based on the available documents.</p>",
                "sources": []
            })

        # Step 3: Generate answer
        answer, sources = generate_answer(question, documents)

        if answer:
            # Convert markdown to HTML for rich rendering
            answer_html = markdown.markdown(answer, extensions=["fenced_code", "tables", "nl2br"])
            return jsonify({"answer": answer_html, "sources": sources})
        else:
            return jsonify({
                "error": "Failed to generate an answer. Please try again."
            }), 500

    except Exception as e:
        print(f"API error: {e}")
        return jsonify({"error": "An internal error occurred. Please try again."}), 500


# ─── Entry Point ────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🚀 AI Search UI running at: http://localhost:8000")
    print("Press Ctrl+C to stop the server.\n")
    try:
        app.run(host="0.0.0.0", port=8000, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped.")
