import os
from pinecone.grpc import PineconeGRPC as Pinecone
from dotenv import load_dotenv
import requests

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
EMBEDDING_MODEL_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-large-en-v1.5"



pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
# Step 2: Connect to your specific index using the host URL
index = pc.Index(
    name=os.getenv("PINECONE_INDEX_NAME"),
    host=os.getenv("PINECONE_HOST")
)

def get_embedding(text: str) -> list:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": text, "options": {"wait_for_model": True}}
    
    response = requests.post(EMBEDDING_MODEL_URL, headers=headers, json=payload)
    
    # Add these two debug lines
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")  # first 200 chars only
    
    if response.status_code != 200:
        raise Exception(f"Embedding failed: {response.status_code} - {response.text}")
    
    embedding = response.json()
    
    if isinstance(embedding[0], list):
        embedding = embedding[0]
    
    print(f"✅ Embedding created! Vector size: {len(embedding)}")
    return embedding

def store_note(note_id: str, title: str, content: str, metadata: dict = {}):
    """Save a note into Pinecone"""
    
    # Combine title + content for better search
    combined_text = f"{title}. {content}"
    vector = get_embedding(combined_text)
    
    # Store with rich metadata
    index.upsert(vectors=[{
        "id": note_id,
        "values": vector,
        "metadata": {
            "title": title,          # Store separately
            "content": content,      # Store separately
            "text": combined_text,   # For search display
            **metadata               # created_at, tags, etc.
        }
    }])
    print(f"✅ Note '{note_id}' stored in Pinecone!")

def search_notes(query: str, top_k: int = 3) -> list:
    """Find the most relevant notes for a given question"""
    query_vector = get_embedding(query)
    
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    
    matches = []
    for match in results['matches']:
        matches.append({
            "score": match['score'],
            "title": match['metadata'].get('title', ''),      # ← Add title
            "content": match['metadata'].get('content', ''),  # ← Add content
            "text": match['metadata'].get('text', '')         # Keep for backward compatibility
        })
        print(f"   Found: {match['metadata'].get('title', '')} (score: {match['score']:.2f})")
    
    return matches

def test_connection():
    """Just to verify everything works"""
    stats = index.describe_index_stats()
    print("✅ Pinecone connected!")
    print(f"   Total vectors stored: {stats['total_vector_count']}")
    return stats

# Run this file directly to test
if __name__ == "__main__":
    test_connection()
    
    # Test embedding
    #sample_text = "Today I learned about machine learning"
    #vector = get_embedding(sample_text)
    #print(f"First 5 numbers of vector: {vector[:5]}")

    # 2. Store 2 sample notes
    store_note("note_001", "I have a meeting with the design team on Friday at 3pm")
    store_note("note_002", "My gym routine: chest on Monday, legs on Wednesday, back on Friday")
    store_note("note_003", "Machine learning is a subset of AI that learns from data patterns")

    # 3. Search for a relevant note
    print("\n🔍 Searching for notes about 'gym'...")
    results = search_notes("What is my workout schedule?")
    for r in results:
        print(f"Score: {r['score']:.2f} | Note: {r['text']}")
