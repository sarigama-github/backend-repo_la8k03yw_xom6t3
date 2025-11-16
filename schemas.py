"""
Database Schemas for Legal Management System

Each Pydantic model below represents a MongoDB collection. The collection
name is the lowercase of the class name (e.g., Case -> "case").

These schemas will be returned by GET /schema for external tools/viewers.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict
from datetime import datetime

# Core entities (Mandatory)

class Client(BaseModel):
    name: str = Field(..., description="Client full name or organization")
    email: Optional[str] = Field(None, description="Primary email")
    phone: Optional[str] = Field(None, description="Primary phone number")
    address: Optional[str] = Field(None, description="Mailing address")
    type: Literal["individual", "organization"] = Field("individual", description="Client type")
    notes: Optional[str] = Field(None, description="Internal notes")
    status: Literal["active", "inactive", "prospect"] = Field("active")

class Case(BaseModel):
    title: str = Field(..., description="Case title")
    description: Optional[str] = Field(None, description="Case description")
    client_id: str = Field(..., description="Reference to client _id as string")
    matter_number: Optional[str] = Field(None, description="Internal matter/case number")
    practice_area: Optional[str] = Field(None, description="e.g., Corporate, Litigation, IP")
    status: Literal["open", "closed", "on_hold"] = Field("open")
    priority: Literal["low", "medium", "high", "urgent"] = Field("medium")
    opened_at: Optional[datetime] = Field(default=None)
    closed_at: Optional[datetime] = Field(default=None)
    assignees: List[str] = Field(default_factory=list, description="User ids assigned")
    tags: List[str] = Field(default_factory=list)

class Task(BaseModel):
    case_id: Optional[str] = Field(None, description="Related case id if any")
    title: str = Field(...)
    description: Optional[str] = Field(None)
    assignee_id: Optional[str] = Field(None)
    status: Literal["todo", "in_progress", "done"] = Field("todo")
    priority: Literal["low", "medium", "high", "urgent"] = Field("medium")
    due_date: Optional[datetime] = Field(None)
    checklist: List[Dict[str, object]] = Field(default_factory=list, description="[{text, done}]")

class Invoice(BaseModel):
    client_id: str = Field(..., description="Client id")
    case_id: Optional[str] = Field(None, description="Case id")
    number: Optional[str] = Field(None, description="Invoice number")
    currency: Literal["USD", "EUR", "GBP", "AUD", "CAD", "INR", "JPY", "CNY"] = Field("USD")
    items: List[Dict[str, object]] = Field(default_factory=list, description="[{description, hours, rate, amount}]")
    status: Literal["draft", "sent", "paid", "overdue", "void"] = Field("draft")
    issued_at: Optional[datetime] = Field(None)
    due_at: Optional[datetime] = Field(None)
    notes: Optional[str] = Field(None)
    total: Optional[float] = Field(None, ge=0)

class Setting(BaseModel):
    key: str = Field(..., description="Setting key")
    value: Dict[str, object] = Field(default_factory=dict, description="Arbitrary JSON value")
    scope: Literal["org", "user"] = Field("org")
    user_id: Optional[str] = Field(None, description="User id if scope=user")

# Optional modules

class LegalDocument(BaseModel):
    title: str
    content: str = Field(..., description="Full text of the legal document")
    jurisdiction: Optional[str] = Field(None)
    practice_area: Optional[str] = Field(None)
    doc_type: Optional[str] = Field(None, description="e.g., statute, case_law, contract, brief")
    year: Optional[int] = Field(None)
    source: Optional[str] = Field(None, description="Source or citation")
    tags: List[str] = Field(default_factory=list)

class Report(BaseModel):
    name: str
    description: Optional[str] = None
    params: Dict[str, object] = Field(default_factory=dict)
    generated_at: Optional[datetime] = None
    data: Dict[str, object] = Field(default_factory=dict)

class AssistantMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = "user"
    content: str
    conversation_id: Optional[str] = None
    related_case_id: Optional[str] = None

# Minimal user schema (for assignment references)
class User(BaseModel):
    name: str
    email: str
    is_active: bool = True
