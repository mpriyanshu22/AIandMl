from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()
pdf_path=Path(__file__).parent/"RelocateHub_Project_Report2.pdf"

loader = PyPDFLoader(file_path = pdf_path)
docs=loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(docs)
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
#ingestion
vector_store = QdrantVectorStore.from_documents(
    documents=[],
    url="http://localhost:6333",
    collection_name="learning_new_langchain",
    embedding=embeddings,
)
vector_store.add_documents(documents=texts)
#retrieval
retriever= QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_new_langchain",
    embedding=embeddings,
)
query=input("> ")
relevant_chunks=retriever.similarity_search(
    query=query
)
context = "\n\n".join(doc.page_content for doc in relevant_chunks)
system_prompt=f"""
you are an helpfull ai assistant who responds based on the available context
context:
{context}
"""

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)

response = llm.invoke(
    system_prompt + "\n\nQuestion: {query}"
)

print(response.content)
# print("relevant chunks",relevant_chunks)
# print("docs",len(docs))
# print("split",len(texts))
