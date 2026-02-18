from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
from typing import List, Optional
from pydantic import BaseModel
import agents
import json
from temporal.worker import start_worker
import asyncio
from config import Config
from temporal import create_waiting_job, start_job_with_diary, terminate_job
import database as db

# ------------------ INIT ------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    asyncio.create_task(start_worker())
    yield
    # shutdown (optional later)
    
app = FastAPI(lifespan=lifespan)

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
  key = db.message_db.format_key(info['session_id'])
  redis_client = db.message_db.get_client()
  
  # Check for exist
  if redis_client.exists(key):
    raise HTTPException(
      status_code=409,
      detail="Session already exists"
      )
  
  system_prompt = agents.chatbot.format_system_prompt(info)
  formatted_input = format_msg("system", system_prompt)
  response = agents.chatbot.get_response(history=[], message=formatted_input)
  redis_client.set(key, json.dumps([formatted_input, format_msg("assistant", response["content"])]))
  
  # print(response)
  asyncio.run(create_waiting_job(session_id=info['session_id'],
                     user_background=info['background'],
                     user_status=info['current_state'],
                     user_diary_summary_1=info['yesterday_summary']))
  
  return response

@app.post("/sessions/{session_id}/messages", response_model=dict)
def add_messages(session_id: str, body: MessageBody):
  """
  Add new messages to a session
  """
  key = db.message_db.format_key(session_id)
  redis_client = db.message_db.get_client()
  msg_history = redis_client.get(key)
  if not msg_history:
    raise HTTPException(status_code=404, detail="Session not found")
  
  msg_history = json.loads(msg_history)
  formatted_input = format_msg("user", body.content)
  response = agents.chatbot.get_response(history=msg_history, message=formatted_input)
  redis_client.set(key, json.dumps(msg_history+[formatted_input, format_msg("assistant", response["content"])]))
  
  # Check for ending trigger
  if response['diary']:
    asyncio.run(start_job_with_diary(session_id=session_id, user_diary=response['diary']))
  
  return response

@app.delete("/sessions/{session_id}", response_model=dict)
def delete_session(session_id: str):
  key = db.message_db.format_key(session_id)
  redis_client = db.message_db.get_client()
  if not redis_client.exists(key):
    raise HTTPException(status_code=404, detail="Session not found")
  
  redis_client.delete(key)
  asyncio.run(terminate_job(session_id))
  
  return {"status": "ok", "session_id": session_id}

# ------------------ RUN ------------------
if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", **Config.APP)