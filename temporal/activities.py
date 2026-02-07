from temporalio import activity
from typing import List
import agents

@activity.defn
async def diary_summary_agent(user_diary: str, session_id: str) -> str:
    # Execution
    summarized_diary = agents.summarizer.get_diary_summary(user_diary)
    
    # Send update to API (summaried_diary, session_id)

    return summarized_diary

@activity.defn
async def past_week_diary_summary_agent(user_diary_sum_0: str, user_diary_sum_1:str, session_id: str) -> str:
    # Ingrediant preparation
    summaries = [f"Diary {i}" for i in range(3, 6 + 1)] # Get from API
    summaries = [user_diary_sum_0, user_diary_sum_1, *summaries]
    
    # Execution
    weekly_summarized = agents.summarizer.get_pw_diary_summary(user_diary)
    
    # Send update to API (weekly_summaried, session_id)
    
    return weekly_summarized

@activity.defn
async def overall_status_agent(user_status: str, user_diary: str, session_id: str) -> str:
    # Execution
    new_user_status = agents.longterm.get_overall_status(user_status, user_diary)
    
    # Send update to API (new_user_status, session_id) if nessascary
    if new_user_status != user_status:
        pass
    
    return new_user_status

@activity.defn
async def background_agent(user_background: str, user_diary: str, session_id: str) -> str:
    # Execution
    new_user_background = agents.longterm.get_background(user_background, user_diary)
    
    # Send update to API (new_user_status, session_id) if nessascary
    if new_user_background != user_background:
        pass

    return new_user_background