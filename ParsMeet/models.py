from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class User:
    id: str
    username: str

@dataclass
class Room:
    id: str
    name: str
    created_at: datetime
    participants: List[User] = field(default_factory=list)

@dataclass
class CodePayload:
    language: str
    code: str