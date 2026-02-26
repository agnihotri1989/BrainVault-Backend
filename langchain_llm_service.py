import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import PromptTemplate
from langchain_pinecone_service import vectorstore
import requests
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

# Setup the LLM model
# llm = HuggingFaceEndpoint(
#     repo_id="deepset/roberta-base-squad2",
#     huggingfacehub_api_token=HF_TOKEN,
#     task="question-answering"
# )

# Step 1 - Your WORKING roberta call wrapped in a function
def call_roberta(input: dict) -> str:
    question = input["question"]
    context = input["context"]
    
    response = requests.post(
        "https://router.huggingface.co/hf-inference/models/deepset/roberta-base-squad2",
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json={
            "inputs": {
                "question": question,
                "context": context
            },
            "options": {"wait_for_model": True}
        }
    )
    result = response.json()
    return result.get("answer", "I couldn't find an answer!")

llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    huggingfacehub_api_token=HF_TOKEN,
    task="text2text-generation",
    max_new_tokens=256
)
# Step 1 - Setup retriever from vectorstore
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Step 2 - Setup prompt template
prompt = PromptTemplate.from_template("""
Use the following notes to answer the question.
                                      
Context: {context}
Question: {question}
Answer:
""")

# Step 3 - Helper to format retrieved docs
def format_docs(docs):
    return " ".join([doc.page_content for doc in docs])

# Step 4 - Build the LCEL chain using | pipe!
# chain = (
#     {
#         "context": retriever | format_docs,  # search Pinecone → format results
#         "question": RunnablePassthrough()    # pass question as is
#     }
#     | prompt                                 # build prompt with context + question
#     | llm                                    # send to HuggingFace model
# )

# Step 4 - LCEL chain with RunnableLambda wrapping roberta!
chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | RunnableLambda(call_roberta)  # 👈 your working roberta call!
)


def ask_question(question: str) -> dict:
    try:
        # ONE line to get the answer! 🎯
        answer = chain.invoke(question)
        
        print(f"✅ Answer: {answer}")
        return {"answer": answer, "source": "langchain"}
    
    except Exception as e:
        import traceback
        traceback.print_exc()  
        print(f"❌ Full Error: {repr(e)}")
        return {"answer": f"Error: {str(e)}"}