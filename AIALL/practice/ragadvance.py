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
You are a search query generator.

Generate 5 different search queries for retrieving
relevant documents.

The queries should be semantically different while
preserving the original meaning.

Question:
{user_query}

Return ONLY the queries.
One query per line.
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
    retrieved_list = list(executor.map(retrieve, queries))

# --------------------------------------------------
# Step 3 : Merge Results
# --------------------------------------------------

all_docs = []

for docs in retrieved_list:
    all_docs.extend(docs)

# --------------------------------------------------
# Step 4 : Remove Duplicates
# --------------------------------------------------

unique_docs = list(
    {doc.page_content: doc for doc in all_docs}.values()
)

print("\nRetrieved:", len(all_docs))
print("Unique:", len(unique_docs))

# --------------------------------------------------
# Step 5 : Build Context
# --------------------------------------------------

# for doc in unique_docs:
#     print("\n--- Retrieved chunk ---")
#     print(doc.metadata)
#     print(doc.page_content)

context = "\n\n".join(
    doc.page_content
    for doc in unique_docs
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