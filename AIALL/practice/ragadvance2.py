from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)
from langchain_qdrant import QdrantVectorStore

load_dotenv()

# --------------------------------------------------
# Load PDF
# --------------------------------------------------

pdf_path = Path(__file__).parent / "RelocateHub_Project_Report2.pdf"

loader = PyPDFLoader(pdf_path)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

texts = splitter.split_documents(docs)

# --------------------------------------------------
# Embedding Model
# --------------------------------------------------

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview"
)

# --------------------------------------------------
# Uncomment once for ingestion
# --------------------------------------------------


vector_store = QdrantVectorStore.from_documents(
    documents=texts,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="learning_langchain",
)


# --------------------------------------------------
# Existing Vector Store
# --------------------------------------------------

vector_store = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_langchain",
    embedding=embeddings,
)

# --------------------------------------------------
# LLM
# --------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)

# --------------------------------------------------
# User Question
# --------------------------------------------------
query=input("> ")
user_query = query

# --------------------------------------------------
# Step 1 : Generate Multiple Search Queries
# --------------------------------------------------

rewrite_prompt = f"""
You are an expert search query generator for a Retrieval-Augmented Generation (RAG) system.

Generate 5 semantically different search queries for retrieving information
from a project report.

Rules:
- Keep every query related to the original question.
- Preserve important entities like project names.
- Use different wording, synonyms, and levels of detail.
- Return ONLY the queries, one per line.

Question:
{user_query}
"""

rewrite_response = llm.invoke(rewrite_prompt)

queries = [
    q.strip("-• ").strip()
    for q in rewrite_response.content.split("\n")
    if q.strip()
]

print("=" * 60)
print("Generated Queries")
print("=" * 60)

for i, q in enumerate(queries, 1):
    print(f"{i}. {q}")

# --------------------------------------------------
# Step 2 : Parallel Retrieval
# --------------------------------------------------

def retrieve(query):
    return vector_store.similarity_search(
        query=query,
        k=3,
    )

with ThreadPoolExecutor(max_workers=len(queries)) as executor:
    retrieved_lists = list(executor.map(retrieve, queries))
from collections import defaultdict

# --------------------------------------------------
# Step 3 + 4 : Reciprocal Rank Fusion (RRF)
# --------------------------------------------------

k = 60

rrf_scores = defaultdict(float)
doc_map = {}

for retrieved_docs in retrieved_lists:

    for rank, doc in enumerate(retrieved_docs, start=1):

        # Use page content as the unique identifier
        doc_id = doc.page_content

        # Save the document
        doc_map[doc_id] = doc

        # RRF score
        rrf_scores[doc_id] += 1 / (k + rank)

# Sort documents by descending RRF score
sorted_docs = sorted(
    rrf_scores.items(),
    key=lambda x: x[1],
    reverse=True
)

# Keep the top N documents
TOP_K = 5

final_docs = [
    doc_map[doc_id]
    for doc_id, score in sorted_docs[:TOP_K]
]

print("\nRRF Ranking")
print("=" * 40)

for q, docs in zip(queries, retrieved_lists):

    print(f"\nQuery: {q}")

    for rank, doc in enumerate(docs, start=1):
        print(f"{rank}. {doc.page_content[:100]}")

print("\nSelected Documents:", len(final_docs))

# --------------------------------------------------
# Step 5 : Build Context
# --------------------------------------------------

context = "\n\n".join(
    doc.page_content
    for doc in final_docs
)
# --------------------------------------------------
# Step 6 : Final Answer Generation
# --------------------------------------------------

system_prompt = f"""
You are a helpful AI assistant.

Answer ONLY from the provided context.

If the answer cannot be found in the context,
say "I don't know."

Context:
{context}
"""

response = llm.invoke(
    system_prompt + f"\n\nQuestion:\n{user_query}"
)

print("\n" + "=" * 60)
print("FINAL ANSWER")
print("=" * 60)
print(response.content)