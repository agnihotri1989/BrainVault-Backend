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

def store_note(note_id: str, title: str, content: str, user_id: int, metadata: dict = {}):
    """
    Store a note in Pinecone with user_id for filtering.
    
    Args:
        note_id: Unique identifier for the note
        title: Note title
        content: Note content
        user_id: ID of the user who owns this note (NEW!)
        metadata: Additional metadata
    
    Returns:
        bool: True if successful
    """
    
    # Step 1 - Combine title + content (same as before!)
    combined_text = f"{title}. {content}"
    
    # Step 2 - Create a Document object
    doc = Document(
        page_content=combined_text,
        metadata={
            "title": title,
            "content": content,
            "text": combined_text,
            "user_id": user_id,  # ← NEW: Tag note with user ID
            **metadata  # Include any additional metadata passed in
        }
    )
    
    # Step 3 - LangChain handles embed + store in ONE line!
    vectorstore.add_documents([doc], ids=[note_id])
    print(f"✅ Note '{note_id}' stored via LangChain!")
    return True

# ✅ CHANGED: Added user_id parameter and metadata filtering
def search_notes(query: str, user_id: int, top_k: int = 3) -> dict:
    """
    Search notes in Pinecone filtered by user_id.
    Each user only sees their own notes.
    
    Args:
        query: Search query string
        user_id: ID of the user performing the search (NEW!)
        top_k: Number of results to return
    
    Returns:
        dict: Contains 'matches' and 'answer' for LLM context
    """
    
    # ✅ NEW: Create metadata filter to only search this user's notes
    # This is the KEY change - Pinecone will only return notes where user_id matches
    filter_dict = {"user_id": {"$eq": user_id}}
    
    # ✅ CHANGED: Added filter parameter to similarity_search
    # LangChain handles embed + search + filter in ONE line!
    results = vectorstore.similarity_search(
        query, 
        k=top_k,
        filter=filter_dict  # ← NEW: Only search this user's notes!
    )
    
    matches = []
    for doc in results:
        matches.append({
            "title": doc.metadata.get('title', ''),
            "content": doc.metadata.get('content', ''),
            "text": doc.page_content
        })
        print(f"   Found for user {user_id}: {doc.metadata.get('title', '')}")
    
    # ✅ NEW: Return structured response with answer context
    if matches:
        # Create context from matches for LLM
        context = "\n\n".join([
            f"Title: {m['title']}\nContent: {m['content']}" 
            for m in matches
        ])
        answer = f"Found {len(matches)} relevant notes:\n\n{context}"
    else:
        answer = "No notes found matching your search."
    
    return {
        "matches": matches,
        "answer": answer,
        "count": len(matches)
    }