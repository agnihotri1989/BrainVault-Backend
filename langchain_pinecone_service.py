import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
index = os.getenv("PINECONE_INDEX_NAME")

# Step 1 - Setup Embedding Model
embedding_model = HuggingFaceEndpointEmbeddings(
    model=EMBEDDING_MODEL,
    huggingfacehub_api_token=HF_TOKEN
)
print(hasattr(embedding_model, "embed_documents"))
print(hasattr(embedding_model, "embed_query"))
# Step 2 - Connect to Pinecone with embedding model attached
vectorstore = PineconeVectorStore(
    index_name=index,
    embedding=embedding_model
)

def store_note(note_id: str, title: str, content: str, metadata: dict = {}):
    
    # Step 1 - Combine title + content (same as before!)
    combined_text = f"{title}. {content}"
    
    # Step 2 - Create a Document object
    doc = Document(
        page_content=combined_text,
        metadata={
            "title": title,
            "content": content,
            "text": combined_text,
            **metadata
        }
    )
    
    # Step 3 - LangChain handles embed + store in ONE line!
    vectorstore.add_documents([doc], ids=[note_id])
    print(f"✅ Note '{note_id}' stored via LangChain!")
    return True

def search_notes(query: str, top_k: int = 3) -> list:
    
    # LangChain handles embed + search + format in ONE line!
    results = vectorstore.similarity_search(query, k=top_k)
    
    matches = []
    for doc in results:
        matches.append({
            "title": doc.metadata.get('title', ''),
            "content": doc.metadata.get('content', ''),
            "text": doc.page_content
        })
        print(f"   Found: {doc.metadata.get('title', '')}")
    
    return matches