from typing import List
from ollama import chat
import json

SYSTEM_PROMPT_1 = """
You are the **AI diary summarizer**.
- Your task is to **condense today's diary entry into a short, information-rich summary that captures the most important events, emotions, and reflections.
- Your goal is to **preserve meaning while minimizing token usage**. The summary will later be used by another AI agent as background context under “Yesterday’s summary”.

**Input**
**Today's diary entry**: {diary}

**Instructions**
- Summarize today’s diary entry into **2–4 concise sentences (max 80 words)**.
- Focus on the **key events, emotions, insights, and takeaways**.
- **Exclude filler language**, redundant phrasing, or extended reflection.
- Maintain a **neutral, clear, and factual tone** while subtly reflecting the emotional essence of the day.
- The goal is to **reduce token usage** while ensuring that tomorrow’s diary agent can understand what happened and how I felt.
"""

SYSTEM_PROMPT_2 = """
You are the **AI diary summarizer**.
- Your task is to **condense past week diary entries into a short, information-rich summary that captures the most important events, emotions, and reflections.
- Your goal is to **preserve meaning while minimizing token usage**. The summary will later be used by another AI agent as background context under “Past week’s summary”.

**Input**
**Past week diary entries (as a JSON arrays)**: {diaries}

**Instructions**
- Summarize past week diary entries into **2–4 concise sentences (max 100 words)**.
- Focus on the **key events, emotions, insights, and takeaways**.
- **Exclude filler language**, redundant phrasing, or extended reflection.
- Maintain a **neutral, clear, and factual tone** while subtly reflecting the emotional essence of the day.

**Output format**
A summary of past week diary entries
"""

# ------------------ FUNCTIONALITY ------------------
def get_diary_summary(entry: str, model="gemma3:4b"):
  # Get the model response
  response = chat(model='gemma3:4b', messages=[{
    'role': 'system',
    'content': SYSTEM_PROMPT_1.format(diary=entry)}],think=False)
  
  return response.message.content;

def get_pw_diary_summary(entries: List[str], model="gemma3:4b"):
  # Get the model response
  response = chat(model='gemma3:4b', messages=[{
    'role': 'system',
    'content': SYSTEM_PROMPT_2.format(diaries=json.dumps(entries))}],think=False)
  
  return response.message.content;