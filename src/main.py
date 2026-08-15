from document_processor import (
    extract_text_from_pdf,
    split_into_chunks
)

from qa_agent import (
    retrieve_relevant_chunks,
    generate_answer
)


def main():
    """Run the document Q&A bot."""

    pdf_path = "documents/employee_handbook.pdf"

    try:
        text = extract_text_from_pdf(pdf_path)
        chunks = split_into_chunks(text)

        print("\n==========================================")
        print("          DOCUMENT Q&A BOT")
        print("==========================================")
        print(f"Loaded File        : {pdf_path}")
        print(f"Document Characters: {len(text)}")
        print(f"Document Chunks    : {len(chunks)}")
        print("==========================================")
        print("Tip: Type 'exit' or 'q' to quit.")
        print("==========================================\n")

        while True:
            try:
                question = input(
                    "\nAsk a question about the document (or 'exit' to quit): "
                ).strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting Document Q&A Bot. Goodbye!")
                break

            if not question:
                continue

            if question.lower() in ("exit", "quit", "q"):
                print("Exiting Document Q&A Bot. Goodbye!")
                break

            relevant_chunks = retrieve_relevant_chunks(
                question,
                chunks
            )

            if not relevant_chunks:
                print(
                    "\nI couldn't find relevant information "
                    "in the document."
                )
                continue

            print("\nGenerating answer using Azure OpenAI...\n")

            answer = generate_answer(
                question,
                relevant_chunks
            )

            print("========== ANSWER ==========\n")
            print(answer)
            print("\n============================")

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")

    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()