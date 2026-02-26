import os
from dotenv import load_dotenv
import requests
from pinecone_service import store_note, search_notes

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL_URL = "https://router.huggingface.co/hf-inference/models/deepset/roberta-base-squad2"

def call_huggingface(prompt: str, context: str = "") -> str:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    if "roberta" in HF_MODEL_URL:
        # Q&A model format
        payload = {
            "inputs": {"question": prompt, "context": context or prompt},
            "options": {"wait_for_model": True}
        }
    else:
        # Text generation format
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 512},
            "options": {"wait_for_model": True}
        }
    
    response = requests.post(HF_MODEL_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"HF API error: {response.status_code} - {response.text}")
    
    result = response.json()
    return result.get("answer", result[0].get("generated_text", "")) if isinstance(result, list) else result.get("answer", result.get("generated_text", ""))

def store_note_langchain(note_id: str, title: str, content: str, metadata: dict = {}):
    try:
        store_note(note_id, title, content, metadata)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def ask_question_langchain(question: str) -> dict:
    try:
        relevant_notes = search_notes(question, top_k=3)
        
        # Format context for roberta - just plain text without bullets
        if relevant_notes:
            context = " ".join([n['text'] for n in relevant_notes])
        else:
            context = "No relevant notes found."
        
        answer = call_huggingface(question, context)
        
        # If answer is empty, return a fallback
        if not answer or answer.strip() == "":
            answer = "I couldn't find a clear answer in your notes."
        
        return {"answer": answer, "source_notes": relevant_notes}
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "source_notes": []}

def test_langchain_connection():
    try:
        print("🔍 Testing connection...")
        test_result = call_huggingface("Say 'Hello, LangChain is working!'")
        print(f"✅ Working! Response: {test_result}")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False