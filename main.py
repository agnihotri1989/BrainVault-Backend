# main.py
from langchain_pinecone_service import store_note, search_notes
from fastapi import FastAPI, Depends, HTTPException, status
from dependencies import get_current_user
from models import User
from auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(
    title="BrainVault API", 
    description="API for BrainVault note management and retrieval", 
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"], 
    allow_credentials=True,
)

# Include authentication routes
app.include_router(auth_router)


# ============ REQUEST/RESPONSE SCHEMAS ============

class ChatRequest(BaseModel):
    """Schema for chat requests"""
    message: str


class ChatResponse(BaseModel):
    """Schema for chat responses"""
    reply: str


# ============ PUBLIC ENDPOINTS ============

@app.get("/")
def read_root(): 
    """Public endpoint - no authentication required"""
    return {"message": "BrainVault API is running!"}


@app.get("/health")
def health_check():
    """Public endpoint - no authentication required""" 
    return {"status": "healthy"}


# ============ PROTECTED ENDPOINTS (USER-SPECIFIC) ============

@app.post("/api/notes")
async def save_note(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Save a note (protected endpoint - user-specific).
    Each user can only save their own notes.
    
    Expected request body:
    {
        "title": "Note title",
        "content": "Note content"
    }
    """
    print(f"User {current_user.email} (ID: {current_user.id}) is saving a note")
    
    title = request.get("title")
    content = request.get("content")
    
    # Validation
    if not title or not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both 'title' and 'content' fields are required"
        )
    
    # Generate unique ID
    note_id = str(uuid.uuid4())
    
    # ✅ Store with user_id - CRITICAL for user-specific filtering
    success = store_note(
        note_id=note_id,
        title=title,
        content=content,
        user_id=current_user.id,  # ← Pass user ID!
        metadata={
            "created_at": datetime.now().isoformat(),
            "user_email": current_user.email  # Optional: For debugging
        }
    )
    
    if success:
        return {
            "message": "Note saved successfully!",
            "note_id": note_id,
            "user": current_user.email
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save note"
        )


@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Search notes using chat (protected endpoint - user-specific).
    Each user can only search their own notes.
    
    Expected request body:
    {
        "message": "What are my meeting notes?"
    }
    """
    print(f"User {current_user.email} (ID: {current_user.id}) is searching: {request.message}")
    
    # ✅ Search only this user's notes by passing user_id
    result = search_notes(
        query=request.message,
        user_id=current_user.id  # ← Pass user ID for filtering!
    )
    
    print(f"Search results for user {current_user.id}: {result['count']} matches")
    
    return ChatResponse(reply=result["answer"])


# ============ OPTIONAL: GET endpoint to list user's notes ============

@app.get("/api/notes")
def get_user_notes(current_user: User = Depends(get_current_user)):
    """
    Get a list of all notes for the current user.
    (Optional - you can implement this later if needed)
    """
    # For now, just return a message
    # Later you can add a list_notes() function to query Pinecone
    return {
        "message": f"Notes for user {current_user.email}",
        "user_id": current_user.id,
        "note": "Use /api/chat to search your notes"
    }