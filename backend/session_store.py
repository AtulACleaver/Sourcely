from dataclasses import dataclass, field
from time import time
import faiss
import uuid


@dataclass
class Session:
    session_id: str
    chunks: list[dict] = field(default_factory=list)
    index: faiss.Index = None
    filename: str = None
    created_at: float = field(default_factory=time)


sessions: dict[str, Session] = {}


def create_session() -> str:
    sid = str(uuid.uuid4())
    sessions[sid] = Session(session_id=sid)
    return sid


def get_session(sid: str) -> Session | None:
    return sessions.get(sid)


def delete_session(sid: str):
    sessions.pop(sid, None)


def cleanup_sessions(max_age_seconds: int = 3600):
    expired = [
        sid for sid, s in sessions.items()
        if time() - s.created_at > max_age_seconds
    ]
    for sid in expired:
        del sessions[sid]
