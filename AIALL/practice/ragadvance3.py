from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)
from langchain_qdrant import QdrantVectorStore

load_dotenv()

# -------------------------------------------------------
# Load PDF
# -------------------------------------------------------

pdf_path = Path(__file__).parent / "RelocateHub_Project_Report2.pdf"

loader = PyPDFLoader(pdf_path)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

texts = splitter.split_documents(docs)

# -------------------------------------------------------
# Embedding Model
# -------------------------------------------------------

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview"
)

# -------------------------------------------------------
# Uncomment ONCE for ingestion
# -------------------------------------------------------


vector_store = QdrantVectorStore.from_documents(
    documents=texts,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="learning_langchain",
)


# -------------------------------------------------------
# Existing Vector Store
# -------------------------------------------------------

vector_store = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_langchain",
    embedding=embeddings,
)

# -------------------------------------------------------
# LLM
# -------------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)

# -------------------------------------------------------
# User Question
# -------------------------------------------------------
query=input("> ")
user_query = query

# -------------------------------------------------------
# Step 1 : Generate Step-Back Question
# -------------------------------------------------------

step_back_prompt = f"""
You are an expert AI assistant.

Your task is to generate ONE broader,
higher-level question that captures
the general concept behind the user's question.

The new question should help retrieve
background information.

Return ONLY the question.

User Question:

{user_query}
"""

step_back_query = llm.invoke(step_back_prompt).content.strip()

print("=" * 70)
print("USER QUESTION")
print("=" * 70)
print(user_query)

print("\n")

print("=" * 70)
print("STEP-BACK QUESTION")
print("=" * 70)
print(step_back_query)

# -------------------------------------------------------
# Step 2 : Retrieve using Original Question
# -------------------------------------------------------

original_docs = vector_store.similarity_search(
    user_query,
    k=4,
)

# -------------------------------------------------------
# Step 3 : Retrieve using Step-Back Question
# -------------------------------------------------------

stepback_docs = vector_store.similarity_search(
    step_back_query,
    k=4,
)

# -------------------------------------------------------
# Step 4 : Merge + Deduplicate
# -------------------------------------------------------

unique_docs = {}

for doc in original_docs + stepback_docs:
    unique_docs[doc.page_content] = doc

final_docs = list(unique_docs.values())

print("\n")
print("=" * 70)
print("RETRIEVED DOCUMENTS")
print("=" * 70)

for i, doc in enumerate(final_docs, 1):

    print(f"\nDocument {i}")
    print("-" * 40)
    print(doc.page_content[:250])

# -------------------------------------------------------
# Step 5 : Build Context
# -------------------------------------------------------

context = "\n\n".join(
    doc.page_content
    for doc in final_docs
)

# -------------------------------------------------------
# Step 6 : Final Answer
# -------------------------------------------------------

system_prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the supplied context.

If the answer is not available,
reply:

"I don't know."

Context:

{context}
"""

response = llm.invoke(

    system_prompt +
    f"\n\nQuestion:\n{user_query}"

)

print("\n")
print("=" * 70)
print("FINAL ANSWER")
print("=" * 70)

print(response.content)