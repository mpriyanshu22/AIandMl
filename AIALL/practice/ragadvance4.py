from pathlib import Path
from dotenv import load_dotenv
import re

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)
from langchain_qdrant import QdrantVectorStore

load_dotenv()

# ==========================================================
# Helper Function for Safe Text Extraction
# ==========================================================
def extract_text(content) -> str:
    """Safely extracts and returns text string from LLM response content block structures."""
    if isinstance(content, list):
        return "".join(
            part if isinstance(part, str) else part.get("text", "") 
            for part in content
        )
    return content if content else ""

# ==========================================================
# Load PDF
# ==========================================================

pdf_path = Path(__file__).parent / "RelocateHub_Project_Report2.pdf"

loader = PyPDFLoader(pdf_path)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

texts = splitter.split_documents(docs)

# ==========================================================
# Embedding Model
# ==========================================================

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview"
)

# ==========================================================
# Uncomment ONLY once for ingestion
# ==========================================================


vector_store = QdrantVectorStore.from_documents(
    documents=texts,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="learning_langchain",
)


# ==========================================================
# Existing Collection
# ==========================================================

vector_store = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_langchain",
    embedding=embeddings,
)

# ==========================================================
# Gemini
# ==========================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite"
)

# ==========================================================
# User Question
# ==========================================================

user_query = "Explain the authentication system in RelocateHub."

# ==========================================================
# STEP 1 : Query Decomposition
# ==========================================================

decompose_prompt = f"""
You are an expert planning assistant.

Break the user's question into
3-5 smaller reasoning steps.

Rules:

- Each step should answer ONE missing piece.
- Later questions should naturally depend on earlier answers.
- Keep the questions concise.
- Preserve important entities.
- Return ONLY the questions.
- One question per line.

Question:

{user_query}
"""

response = llm.invoke(decompose_prompt)
raw_content = extract_text(response.content)

subquestions = []

# Use raw_content instead of response.content
for line in raw_content.splitlines():

    line = line.strip()

    if not line:
        continue

    # remove numbering like 1., 2), 10.
    line = re.sub(r'^\d+[\.\)]\s*', '', line)

    subquestions.append(line)

print("=" * 70)
print("ORIGINAL QUESTION")
print("=" * 70)

print(user_query)

print()

print("=" * 70)
print("DECOMPOSED QUESTIONS")
print("=" * 70)

for i, q in enumerate(subquestions, start=1):
    print(f"{i}. {q}")

# ==========================================================
# STEP 2 : Helper Function
# Rewrite Retrieval Query
# ==========================================================

def rewrite_retrieval_query(previous_findings, current_question):
    
    prompt = f"""
You are a search query optimizer for RAG.

Previous Findings:

{previous_findings}

Current Question:

{current_question}

Generate ONE semantic search query
that will retrieve the most useful
information for answering the
current question.

The query should include useful
context from previous findings
when appropriate.

Return ONLY the search query.
"""

    res = llm.invoke(prompt)
    return extract_text(res.content).strip()

# ==========================================================
# STEP 3 : Helper Function
# Retrieve Documents
# ==========================================================

def retrieve_documents(search_query, k=3):

    docs = vector_store.similarity_search(
        search_query,
        k=k
    )

    return docs

# ==========================================================
# STEP 4 : Helper Function
# Build Context
# ==========================================================

def build_context(documents):

    return "\n\n".join(
        doc.page_content
        for doc in documents
    )

# ==========================================================
# STEP 5 : Helper Function
# Answer One Step
# ==========================================================

def answer_subquestion(
    original_question,
    previous_findings,
    retrieved_context,
    current_question,
):

    prompt = f"""
You are solving a problem step-by-step.

Original Question:

{original_question}

Previous Findings:

{previous_findings}

Retrieved Context:

{retrieved_context}

Current Question:

{current_question}

Instructions:

- Answer ONLY the current question.
- Use the retrieved context.
- Build upon previous findings.
- Do not repeat earlier answers.
- If the answer is unavailable,
  say "I don't know."

Keep the answer under 100 words.
"""

    res = llm.invoke(prompt)
    return extract_text(res.content).strip()

# ==========================================================
# Variables for Sequential Reasoning
# ==========================================================

previous_findings = ""

intermediate_answers = []

# ==========================================================
# STEP 6 : Sequential Retrieval + Reasoning
# ==========================================================

print("\n")
print("=" * 80)
print("SEQUENTIAL REASONING")
print("=" * 80)

for step, question in enumerate(subquestions, start=1):

    print("\n")
    print("=" * 80)
    print(f"STEP {step}")
    print("=" * 80)

    print("\nCurrent Question:")
    print(question)

    # ------------------------------------------------------
    # Rewrite retrieval query using previous findings
    # ------------------------------------------------------

    retrieval_query = rewrite_retrieval_query(
        previous_findings,
        question
    )

    print("\nRetrieval Query:")
    print(retrieval_query)

    # ------------------------------------------------------
    # Retrieve documents
    # ------------------------------------------------------

    docs = retrieve_documents(
        retrieval_query,
        k=3
    )

    context = build_context(docs)

    print("\nRetrieved Chunks:")

    for i, doc in enumerate(docs, start=1):

        print(f"\nChunk {i}")
        print("-" * 50)
        print(doc.page_content[:250])

    # ------------------------------------------------------
    # Answer current question
    # ------------------------------------------------------

    answer = answer_subquestion(
        original_question=user_query,
        previous_findings=previous_findings,
        retrieved_context=context,
        current_question=question,
    )

    print("\nIntermediate Answer:")
    print(answer)

    # ------------------------------------------------------
    # Store findings
    # ------------------------------------------------------

    intermediate_answers.append(answer)

    previous_findings += f"""

Step {step}

Question:
{question}

Answer:
{answer}
"""

# ==========================================================
# STEP 7 : Final Synthesis
# ==========================================================

print("\n")
print("=" * 80)
print("FINAL SYNTHESIS")
print("=" * 80)

final_prompt = f"""
You are an expert AI assistant.

Original User Question:

{user_query}

Below are the findings obtained by
solving the problem step-by-step.

{previous_findings}

Write ONE final answer.

Requirements:

- Combine all findings.
- Remove repetition.
- Write naturally.
- Do not mention intermediate reasoning.
- If some information is missing,
  mention that clearly.
"""

final_answer = llm.invoke(final_prompt)

print("\n")
print("=" * 80)
print("FINAL ANSWER")
print("=" * 80)

print(extract_text(final_answer.content))