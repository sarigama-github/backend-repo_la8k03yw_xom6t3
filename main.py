import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from database import db, create_document, get_documents
from schemas import Client, Case, Task, Invoice, Setting, LegalDocument, AssistantMessage

app = FastAPI(title="Legal Management System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Legal Management System Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or ""
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:20]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:120]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:120]}"
    return response

# Utility function for simple queries

def _query(collection: str, q: Optional[str] = None, extra: Optional[Dict[str, Any]] = None, limit: int = 50):
    filter_dict: Dict[str, Any] = extra.copy() if extra else {}
    if q:
        # naive regex search on some common keys
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"name": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
        ]
    return get_documents(collection, filter_dict, limit)

# Clients (Mandatory)

@app.post("/clients")
def create_client(payload: Client):
    _id = create_document("client", payload)
    return {"id": _id}

@app.get("/clients")
def list_clients(q: Optional[str] = Query(None), limit: int = 50):
    return _query("client", q=q, limit=limit)

# Cases (Mandatory)

@app.post("/cases")
def create_case(payload: Case):
    _id = create_document("case", payload)
    return {"id": _id}

@app.get("/cases")
def list_cases(q: Optional[str] = Query(None), client_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
    extra: Dict[str, Any] = {}
    if client_id:
        extra["client_id"] = client_id
    if status:
        extra["status"] = status
    return _query("case", q=q, extra=extra, limit=limit)

# Tasks (Mandatory)

@app.post("/tasks")
def create_task(payload: Task):
    _id = create_document("task", payload)
    return {"id": _id}

@app.get("/tasks")
def list_tasks(case_id: Optional[str] = None, status: Optional[str] = None, assignee_id: Optional[str] = None, limit: int = 50):
    extra: Dict[str, Any] = {}
    if case_id:
        extra["case_id"] = case_id
    if status:
        extra["status"] = status
    if assignee_id:
        extra["assignee_id"] = assignee_id
    return get_documents("task", extra, limit)

# Billing (Mandatory)

@app.post("/invoices")
def create_invoice(payload: Invoice):
    _id = create_document("invoice", payload)
    return {"id": _id}

@app.get("/invoices")
def list_invoices(client_id: Optional[str] = None, case_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
    extra: Dict[str, Any] = {}
    if client_id:
        extra["client_id"] = client_id
    if case_id:
        extra["case_id"] = case_id
    if status:
        extra["status"] = status
    return get_documents("invoice", extra, limit)

# Settings (Mandatory)

@app.post("/settings")
def create_setting(payload: Setting):
    _id = create_document("setting", payload)
    return {"id": _id}

@app.get("/settings")
def list_settings(scope: Optional[str] = None, user_id: Optional[str] = None, limit: int = 100):
    extra: Dict[str, Any] = {}
    if scope:
        extra["scope"] = scope
    if user_id:
        extra["user_id"] = user_id
    return get_documents("setting", extra, limit)

# Legal Database (100k+ documents ready)

@app.post("/legal-docs")
def create_legal_doc(payload: LegalDocument):
    _id = create_document("legaldocument", payload)
    return {"id": _id}

@app.get("/legal-docs")
def search_legal_docs(q: Optional[str] = Query(None), practice_area: Optional[str] = None, jurisdiction: Optional[str] = None, year: Optional[int] = None, limit: int = 50):
    extra: Dict[str, Any] = {}
    if practice_area:
        extra["practice_area"] = practice_area
    if jurisdiction:
        extra["jurisdiction"] = jurisdiction
    if year:
        extra["year"] = year
    return _query("legaldocument", q=q, extra=extra, limit=limit)

# AI Assistant conversation storage (messages)

@app.post("/assistant/messages")
def add_message(payload: AssistantMessage):
    _id = create_document("assistantmessage", payload)
    return {"id": _id}

@app.get("/assistant/messages")
def list_messages(conversation_id: Optional[str] = None, related_case_id: Optional[str] = None, limit: int = 100):
    extra: Dict[str, Any] = {}
    if conversation_id:
        extra["conversation_id"] = conversation_id
    if related_case_id:
        extra["related_case_id"] = related_case_id
    return get_documents("assistantmessage", extra, limit)

# Schema endpoint to expose available collections

class SchemaResponse(BaseModel):
    collections: List[str]

@app.get("/schema", response_model=SchemaResponse)
def get_schema():
    # Read classes from schemas and convert to collection names
    collections = [
        "client",
        "case",
        "task",
        "invoice",
        "setting",
        "legaldocument",
        "assistantmessage",
    ]
    return {"collections": collections}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
