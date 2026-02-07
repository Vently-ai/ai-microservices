from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from redis import Redis
import agents
import json
from temporal.worker import start_worker
import asyncio

app = FastAPI()
message_db = Redis(
  host="localhost",
  port=6379,
  db=0, # database id = 0
  decode_responses=True # returns strings instead of bytes
)

# ------------------ MODELS ------------------

class NewMessage(BaseModel):
  session_id: str
  content: str
  
class MessageBody(BaseModel):
  content: str
  
class SessionCreate(BaseModel):
    session_id: str
    nickname: str
    background: Optional[str] = "N/A"
    current_state: Optional[str] = "N/A"
    yesterday_summary: Optional[str] = "N/A"
    pastweek_summary: Optional[str] = "N/A"

# ------------------ ROUTES ------------------
format_msg = lambda r, p: { "content": p, "role": r }

@app.post("/sessions", response_model=dict)
def create_new_session(info: SessionCreate):
  """
  Initialize new session
  """
  info = info.dict()
  system_prompt = agents.chatbot.format_system_prompt(info)
  formatted_input = format_msg("system", system_prompt)
  response = agents.chatbot.get_response(history=[], message=formatted_input)
  message_db.set(f"session:{info['session_id']}", json.dumps([formatted_input, format_msg("assistant", response["content"])]))
  
  return response

@app.post("/sessions/{session_id}/messages", response_model=dict)
def add_messages(session_id: str, body: MessageBody):
  """
  Add new messages to a session
  """
  msg_history = message_db.get(session_id)
  if not msg_history:
    raise HTTPException(status_code=404, detail="Session not found")
  
  msg_history = json.loads(msg_history)
  formatted_input = format_msg("user", body.content)
  response = agents.chatbot.get_response(history=msg_history, message=formatted_input)
  message_db.set(f"session:{session_id}", json.dumps(msg_history+[formatted_input, format_msg("assistant", response["content"])]))
  return response

# ------------------ RUN ------------------
@app.on_event("startup")
async def startup():
  asyncio.create_task(start_worker())

if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)