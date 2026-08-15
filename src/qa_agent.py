import os
import re

from dotenv import load_dotenv
from openai import AzureOpenAI


# ============================================================
# LOAD AZURE CONFIGURATION
# ============================================================

load_dotenv()


import math


def retrieve_relevant_chunks(question, chunks, top_k=3):
    """Find the most relevant document chunks for a question using BM25 ranking."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not chunks:
        raise ValueError("No document chunks are available.")

    def tokenize(text):
        return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9_]+\b", text)]

    chunk_tokens = [tokenize(c) for c in chunks]
    total_docs = len(chunks)

    # Document frequency
    df = {}
    for tokens in chunk_tokens:
        for word in set(tokens):
            df[word] = df.get(word, 0) + 1

    # BM25 constants
    k1 = 1.5
    b = 0.75
    avg_doc_len = sum(len(toks) for toks in chunk_tokens) / max(total_docs, 1)

    query_tokens = tokenize(question)
    if not query_tokens:
        return []

    scored_chunks = []

    for index, (chunk, tokens) in enumerate(zip(chunks, chunk_tokens)):
        doc_len = len(tokens)
        score = 0.0

        # Term frequency dictionary for this chunk
        tf_dict = {}
        for token in tokens:
            tf_dict[token] = tf_dict.get(token, 0) + 1

        for q_token in query_tokens:
            if q_token in tf_dict:
                doc_freq = df.get(q_token, 1)
                # BM25 IDF
                idf = math.log(1 + (total_docs - doc_freq + 0.5) / (doc_freq + 0.5))
                tf = tf_dict[q_token]
                score += idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avg_doc_len))))

        if score > 0:
            scored_chunks.append(
                (score, index, chunk)
            )

    scored_chunks.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        {
            "chunk_index": index,
            "score": score,
            "text": chunk
        }
        for score, index, chunk in scored_chunks[:top_k]
    ]


# ============================================================
# AZURE OPENAI CLIENT
# ============================================================

def create_azure_client():
    """Create and validate the Azure OpenAI client."""

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    if not endpoint:
        raise ValueError(
            "AZURE_OPENAI_ENDPOINT is missing from .env"
        )

    if not api_key:
        raise ValueError(
            "AZURE_OPENAI_API_KEY is missing from .env"
        )

    if not api_version:
        raise ValueError(
            "AZURE_OPENAI_API_VERSION is missing from .env"
        )

    return AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version
    )


# ============================================================
# GENERATE GROUNDED ANSWER
# ============================================================

def generate_answer(question, relevant_chunks):
    """Generate an answer using only retrieved document content."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not relevant_chunks:
        return (
            "I couldn't find this information in the document."
        )

    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not deployment:
        raise ValueError(
            "AZURE_OPENAI_DEPLOYMENT is missing from .env"
        )

    context = "\n\n".join(
        result["text"]
        for result in relevant_chunks
    )

    prompt = f"""
You are an enterprise document assistant.

Answer the user's question using ONLY the provided
document context.

Rules:
- Do not use outside knowledge.
- Do not invent facts.
- Do not make assumptions.
- Keep the answer clear and concise.
- If the answer cannot be found in the provided context,
  say exactly:
  "I couldn't find this information in the document."

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}
"""

    client = create_azure_client()

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an enterprise document assistant. "
                    "Answer only from the supplied document context."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_completion_tokens=2000
    )

    # ========================================================
    # AZURE RESPONSE VALIDATION / DEBUG
    # ========================================================

    if not response.choices:
        raise ValueError(
            "Azure OpenAI returned no choices."
        )

    choice = response.choices[0]

    print("\n========== AZURE RESPONSE DEBUG ==========")
    print(f"Finish reason: {choice.finish_reason}")
    print(
        f"Message content: "
        f"{choice.message.content!r}"
    )
    print("==========================================\n")

    answer = choice.message.content

    if not answer or not answer.strip():
        raise ValueError(
            "Azure OpenAI returned no text. "
            f"Finish reason: {choice.finish_reason}"
        )

    return answer.strip()