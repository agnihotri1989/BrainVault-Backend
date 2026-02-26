from langchain_service import store_note_langchain, ask_question_langchain, test_langchain_connection
from langchain_pinecone_service import store_note
from langchain_llm_service import ask_question
from unittest import result
from urllib import response
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv
import uuid
load_dotenv() 
HF_TOKEN = os.getenv("HF_TOKEN")
#base_urlsummry = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
BASEURLQNA = "https://router.huggingface.co/hf-inference/models/deepset/roberta-base-squad2"
HF_URL = "https://router.huggingface.co/hf-inference/models/deepset/minilm-uncased-squad2"
app = FastAPI(title="BrainVault API", description="API for BrainVault note management and retrieval", version="1.0" )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"], 
    allow_credentials=True,)

# question: str = ""           # The user's question
    # note_context: str = ""
# ✅ This defines the shape of data your app will SEND to the server
class ChatRequest(BaseModel):
         # The notes we'll search later (empty for now)
    message: str
# ✅ This defines the shape of data the server will RETURN
class ChatResponse(BaseModel):
    reply: str

@app.get("/")
def read_root():    return {"message": "BrainVault API is running!"}

@app.get("/health")
def health_check(): return {"status": "healthy"}


# Add a new endpoint to save notes
@app.post("/api/notes")
async def save_note(request: dict):
    print("Received note:", request)
    from datetime import datetime
    title = request.get("title")
    content = request.get("content")
    # Basic validation
    # Validation
    if not title or not content:
        return {"error": "Both 'title' and 'content' fields are required"}
    
    # Generate unique ID
    note_id = str(uuid.uuid4())  # e.g., "a3f2b1c4-..."
    
    # Store with metadata
    success = store_note(
        note_id=note_id,
        title=title,
        content=content,
        metadata={"created_at": datetime.now().isoformat()}
    )
    
    if success:
        return {
            "message": "Note saved successfully!",
            "note_id": note_id  # Return ID to Android for syncing
        }
    else:
        return {"error": "Failed to save note"}
    
@app.post("/api/chat")
async def chat(request: ChatRequest):
    
    result = ask_question(request.message)
    print("RESULT:", result)
    return ChatResponse(reply=result["answer"])


# Update your existing /api/chat to use Pinecone context
# @app.post("/api/chat")
# async def chat(request: ChatRequest):
    
#     print("ChatRequest:", request.message)
#     # ── STEP 1: Find relevant notes from Pinecone ──────────────────
#     relevant_notes = search_notes(request.message)
    
#     if relevant_notes:
#         context = "\n".join([f"- {n['text']}" for n in relevant_notes])
#     else:
#         context = "No personal notes found."
    
#     # ── STEP 2: Build a smart prompt with your notes as context ────
#     prompt = f"""Here are some personal notes:
# {context}

# Based on the notes above, answer this question: {request.message}"""

#     # ── STEP 3: Send the prompt to HuggingFace ─────────────────────
#     hf_headers = {"Authorization": f"Bearer {HF_TOKEN}"}
  
    
#     hf_response = requests.post(
#         "https://router.huggingface.co/hf-inference/models/deepset/roberta-base-squad2",                                  # your existing HF URL variable
#         headers=hf_headers,
#        json={
#         "inputs": {
#             "question": request.message,   # 👈 the user's question
#             "context": context             # 👈 your Pinecone notes as context
#         }
#         ,
#         "options": {
#             "wait_for_model": True    # 👈 tells HF to wait until model is ready
#         }
#     }                # 👈 prompt replaces request.message
#     )
#     print("HF_RESPONSE:", hf_response)
    
#     # ── STEP 4: Guard against empty or failed responses ────────────
#     if not hf_response.content:
#         return ChatResponse(reply="AI returned an empty response.")
    
#     if hf_response.status_code != 200:
#         return ChatResponse(reply=f"HuggingFace error: {hf_response.status_code}")
    
#     result = hf_response.json()
#     print("HF_RESULT:", result)
#     # ── STEP 5: Extract the text (facebook/bart-large-cnn returns summary_text) ──
#     #ai_response = result[0].get("summary_text", "Sorry, I could not generate a response.")
#     ai_response = result.get("answer", "Sorry, I could not generate a response.")
#     print("AI_RESULT:", ai_response)
#     # ── STEP 6: Return the final answer ────────────────────────────
#     return ChatResponse(reply=ai_response)
 
# ✅ THE MAIN ENDPOINT - dummy for now, AI-powered later
# @app.post("/api/chat")
# def chat(request: ChatRequest) -> ChatResponse:

#     headers = {"Authorization": f"Bearer {HF_TOKEN}"}
#     payload = {
#         "inputs": request.question,
#         "parameters": {"max_new_tokens": 200}
#     }
#     # Free HuggingFace model (no GPU needed)
#     response = requests.post(
#         "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn",
#         headers=headers,
#         json=payload
#     )
#     print("HF Raw Response:", response.status_code, response.text)
#     print("HF_TOKEN loaded:", HF_TOKEN if HF_TOKEN else "TOKEN IS NONE ❌")
#     result = response.json()
#     # Better error handling
#     #if isinstance(result, list):
#       #  answer = result[0]["summary_text"]
#     #elif "error" in result:
#         #answer = f"HF Error: {result['error']}"  # Shows real error now
#     #else:
#        # answer = str(result)
#     # Extract the answer
#     #answer = result[0]["generated_text"] if isinstance(result, list) else str(result)
#     answer = result[0].get("summary_text") or result[0].get("generated_text") or str(result[0])
#     # 🔲 Dummy response - we'll replace this with real AI in the next step
#     return ChatResponse(answer=answer, source="huggingface") 

@app.get("/test-langchain")
def test_langchain():
    success = test_langchain_connection()
    return {"status": "connected" if success else "failed"}


