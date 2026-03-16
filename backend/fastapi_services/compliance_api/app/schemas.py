from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class BuildCreate(BaseModel):
    rule_key: str = Field(..., max_length=100)
    version: str = Field(..., max_length=20)
    git_commit_hash: Optional[str] = Field(default=None, max_length=40)


class BuildRead(BaseModel):
    id: str
    rule_key: str
    version: str
    git_commit_hash: Optional[str] = None
    status: str
    created_at: datetime


class JobCreate(BaseModel):
    build_id: str
    context: Dict[str, Any]


class JobRead(BaseModel):
    id: str
    build_id: str
    input_hash: str
    status: str
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
