from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.config import config
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.reddit_scraper import RedditScraper
from app.vector_store import VectorStore
from app.rag_engine import RAGEngine
import os

app = FastAPI()

# Initialize components at module level
print("Initializing API components...")

print("Initializing Reddit Scraper...")
scraper = RedditScraper()

print("Initializing Vector Store...")
vector_store = VectorStore()

print("Initializing RAG Engine...")
rag_engine = RAGEngine()

print("Initializing FastAPI application...")

# Get the absolute path to the frontend directory
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# Mount the static frontend files
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
print(f"Mounted frontend directory: {FRONTEND_DIR}")


class Question(BaseModel):
    text: str


class FetchRequest(BaseModel):
    days: int


@app.get("/")
async def read_root():
    print("Serving index.html")
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/status")
async def get_status():
    """Get the current status of stored data"""
    print("Getting system status...")
    try:
        # Get all documents from the collection
        all_docs = vector_store.collection.get()

        if not all_docs or not all_docs["metadatas"]:
            print("No documents found in vector store")
            return {
                "total_documents": 0,
                "date_range": None,
                "oldest_date": None,
                "newest_date": None,
            }

        # Extract dates from metadata
        dates = [meta["post_date"] for meta in all_docs["metadatas"]]
        dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates]

        oldest_date = min(dates).strftime("%Y-%m-%d")
        newest_date = max(dates).strftime("%Y-%m-%d")
        date_range = (max(dates) - min(dates)).days + 1

        print(f"Found {len(all_docs['ids'])} documents spanning {date_range} days")
        return {
            "total_documents": len(all_docs["ids"]),
            "date_range": date_range,
            "oldest_date": oldest_date,
            "newest_date": newest_date,
        }
    except Exception as e:
        print(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_config():
    """Get current LLM configuration"""
    print("⚙️ Getting LLM configuration...")
    return (
        {
            "llm_backend": config.LLM_BACKEND,
            "model_name": config.OPENAI_MODEL_NAME,
        }
        if config.is_openai
        else {
            "llm_backend": config.LLM_BACKEND,
            "model_name": config.OLLAMA_MODEL_NAME,
        }
    )


@app.post("/fetch")
async def fetch_data(request: FetchRequest):
    """Fetch additional days of data"""
    print(f"Fetching {request.days} days of data...")
    try:
        posts = scraper.get_daily_threads(days_back=request.days)
        vector_store.add_documents(posts)
        print("Data fetch completed successfully")
        return {"message": f"Successfully fetched {request.days} days of data"}
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
async def ask_question(question: Question):
    """Ask a question to the RAG system"""
    print(f"Received question: {question.text[:50]}...")
    try:
        results = vector_store.query(question.text)
        response = rag_engine.generate_response(
            question=question.text, context=results["documents"][0]
        )
        print("✅ Response generated successfully")
        return {"response": response}
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_data():
    """Reset the vector store by deleting all documents"""
    print("🗑️ Resetting vector store...")
    try:
        vector_store.delete_collection()
        print("✅ Vector store reset completed")
        return {"message": "Successfully reset vector store"}
    except Exception as e:
        print(f"Error resetting vector store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
