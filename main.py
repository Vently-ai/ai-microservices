from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
from typing import List, Optional
from pydantic import BaseModel
from redis import Redis
import agents
import json
from temporal.worker import start_worker
import asyncio
from config import Config
from temporal import create_waiting_job, start_job_with_diary

# ------------------ INIT ------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    asyncio.create_task(start_worker())
    yield
    # shutdown (optional later)
    
app = FastAPI(lifespan=lifespan)

message_db = Redis(
  **Config.REDIS,
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
format_redis_key = lambda s: f"session:{s}"

@app.post("/sessions", response_model=dict)
def create_new_session(info: SessionCreate):
  """
  Initialize new session
  """
  info = info.dict()
  key = format_redis_key(info['session_id'])
  
  # Check for exist
  if message_db.exists(key):
    raise HTTPException(
      status_code=409,
      detail="Session already exists"
      )
  
  system_prompt = agents.chatbot.format_system_prompt(info)
  formatted_input = format_msg("system", system_prompt)
  response = agents.chatbot.get_response(history=[], message=formatted_input)
  message_db.set(key, json.dumps([formatted_input, format_msg("assistant", response["content"])]))
  
  print(response)
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
  msg_history = message_db.get(format_redis_key(session_id))
  if not msg_history:
    raise HTTPException(status_code=404, detail="Session not found")
  
  msg_history = json.loads(msg_history)
  formatted_input = format_msg("user", body.content)
  response = agents.chatbot.get_response(history=msg_history, message=formatted_input)
  message_db.set(format_redis_key(session_id), json.dumps(msg_history+[formatted_input, format_msg("assistant", response["content"])]))
  
  # Check for ending trigger
  if response['diary']:
    asyncio.run(start_job_with_diary(session_id=session_id, user_diary=response['diary']))
  
  return response


# ------------------ RUN ------------------
if __name__ == "__main__":
  import uvicorn
  uvicorn.run("main:app", **Config.APP)