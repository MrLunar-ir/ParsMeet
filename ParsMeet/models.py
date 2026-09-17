from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class User:
    id: str
    username: str = ""
    first_name: str = ""
    is_bot: bool = False
    is_admin: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "User":
        return cls(id=str(d.get("id", "")), username=d.get("username", ""), first_name=d.get("first_name", ""), is_bot=d.get("is_bot", False), is_admin=d.get("is_admin", False))

@dataclass
class Chat:
    id: str
    type: str = "private"
    title: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Chat":
        return cls(id=str(d.get("id", "")), type=d.get("type", "private"), title=d.get("title", ""))

@dataclass
class Message:
    message_id: int
    chat: Chat
    from_user: Optional[User]
    text: str = ""
    reply_to: Optional[Dict] = None
    raw: Dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "Message":
        return cls(message_id=d.get("message_id", 0), chat=Chat.from_dict(d.get("chat", {})), from_user=User.from_dict(d.get("from", {})) if d.get("from") else None, text=d.get("text", ""), reply_to=d.get("reply_to_message"), raw=d)

@dataclass
class Update:
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[Dict] = None

    @classmethod
    def from_dict(cls, d: dict) -> "Update":
        return cls(update_id=d.get("update_id", 0), message=Message.from_dict(d["message"]) if "message" in d else None, callback_query=d.get("callback_query"))

@dataclass
class Photo:
    file_id: str
    width: int = 0
    height: int = 0
    caption: str = ""

@dataclass
class Document:
    file_id: str
    file_name: str = ""
    mime_type: str = ""
    caption: str = ""