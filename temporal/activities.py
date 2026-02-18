from temporalio import activity
from typing import List
import agents
import database as db
import requests
from config import Config

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {Config.BACKEND["api_key"]}"
}

@activity.defn
async def diary_summary_agent(user_diary: str, session_id: str) -> str:
    # Execution
    summarized_diary = agents.summarizer.get_diary_summary(user_diary)
    
    # Send update to API (summaried_diary, session_id)
    url = f"{Config.BACKEND["base_url"]}/sessions/{session_id}/user/diary"
    requests.post(url, json={
        "content": user_diary,
        "summarized_content": summaried_diary
    }, headers=headers)

    return summarized_diary

@activity.defn
async def past_week_diary_summary_agent(user_diary_sum_0: str, user_diary_sum_1:str, session_id: str) -> str:
    # Ingrediant preparation
    url1 = f"{Config.BACKEND["base_url"]}/sessions/{session_id}/user/sum_diary"
    summaries_response = requests.get(url1, params={"n": 5, "sf": 2}, headers=headers) # Get 5 entries, seek first 2 entries
    entries = summaries_response.json().get("entries") or []

    summaries = [e for e in entries if e] # Remove any falsy value
    summaries = [user_diary_sum_0, user_diary_sum_1, *summaries] # Concat new one
    
    # Execution
    weekly_summarized = agents.summarizer.get_pw_diary_summary(summaries)
    
    # Send update to API (weekly_summaried, session_id)
    url2 = f"{Config.BACKEND["base_url"]}/sessions/{session_id}/user/state"
    requests.put(url2, json={
        "pastweek_summary": weekly_summarized
    }, headers=headers)
    
    return weekly_summarized

@activity.defn
async def overall_status_agent(user_status: str, user_diary: str, session_id: str) -> str:
    # Execution
    new_user_status = agents.longterm.get_overall_status(user_status, user_diary)
    
    # Send update to API (new_user_status, session_id) if nessascary
    if new_user_status != user_status:
        url = f"{Config.BACKEND["base_url"]}/sessions/{session_id}/user/state"
        requests.put(url, json={
            "current_state": weekly_summarized
        }, headers=headers)
    
    return new_user_status

@activity.defn
async def background_agent(user_background: str, user_diary: str, session_id: str) -> str:
    # Execution
    new_user_background = agents.longterm.get_background(user_background, user_diary)
    
    # Send update to API (new_user_status, session_id) if nessascary
    if new_user_background != user_background:
        url = f"{Config.BACKEND["base_url"]}/sessions/{session_id}/user/state"
        requests.put(url, json={
            "background": weekly_summarized
        }, headers=headers)

    return new_user_background

@activity.defn
async def terminate_session_in_redis(session_id: str):
    redis_client = db.message_db.get_client()
    redis_client.delete(db.message_db.format_key(session_id))