from pydantic import BaseModel
from typing import Optional
from enum import Enum

class MessageType(str, Enum):
    TRANSCRIPT = "transcript"
    ERROR = "error"
    STATUS="status"

class TranscriptMessage(BaseModel):
    type: MessageType=MessageType.TRANSCRIPT
    text:str
    is_final:bool=True
    latency_ms:int
    session_id:str

class StatusMessage(BaseModel):
    type: MessageType=MessageType.STATUS
    status:str
    session_id:str

class ErrorMessage(BaseModel):
    type: MessageType=MessageType.ERROR
    error:str
    session_id:str