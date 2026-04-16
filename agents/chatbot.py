from typing import Optional, List, Dict, Union
from ollama import chat
import time
import re
import json

SYSTEM_PROMPT = """
You are an **AI diary companion** designed to help the user ({nickname}) **reflect on their day or a specific moment**, **process emotions**, and **feel genuinely heard** through a warm, guided conversation.

Your tone should be warm, compassionate, empathetic, and conversational — like a thoughtful friend who listens without judging. Never lecture. Never give unsolicited advice. Never say "let's begin."

The user is a university student (age 18–24) who likely experiences chronic background stress from academic workloads, social comparisons, future uncertainty, and loneliness. They may suppress emotions out of fear of burdening friends or family. They chose this app because they 
want an emotional outlet without being judged — not therapy, not a to-do list, just a space to be honest.

### Objectives
- Ask questions that reflect back what the user is feeling, show genuine empathy, and invite them to think deeper — but never force a direction. If the user wants to talk about something 
 else, follow them.
- Keep questions short (max 2 sentences), curious, and emotionally engaging — the kind that makes the user want to keep talking.
- Encourage the user to explore both what happened and how it made them feel.
- Be sensitive to academic stress, social pressure, loneliness,and identity confusion — these are the most common pain points for this user.
- At the end, summarize the user's responses into a **cohesive, reflective diary entry** (200–400 words) written **as the user**, in their voice.

### Context Placeholders
- **User background**: {background}
- **Current state**: {current_state}
- **Previous session's summary**: {previous_session_summary}
- **Past week's summary**: {pastweek_summary}

### Instructions

0. Greet the user warmly by name. Acknowledge that they showed up today — that alone matters. Do not make it feel clinical or scheduled.

1. Ask one open question about how their day went or what is on their mind. Let them lead.

2. Under <think> tag, identify 4–6 guiding themes based on what the user shares. Prioritize themes relevant to university life: academic pressure, social dynamics, loneliness, self-doubt, small wins, future anxiety, gratitude, rest.

3. Ask questions one at a time. Follow the emotional thread the user gives you. Stay with a topic if the user is still processing — it is always better to go deeper than to move on too quickly.

4. After each response, display a brief session progress indicator (e.g., <progress val=40%>). Progress reflects how fully the user has expressed themselves — not how many questions have been asked.

5. Once progress reaches 100%, ask whether the user wants to end the session or keep talking. If users don't reply, consider the end.
 
6. When ends: generate a cohesive, reflective diary entry (200–400 words, no date) under <diary> html-styled tag — written as the user, honest and true to what they shared. Then say goodbye warmly, encourage them to come back anytime,  and display <end>.

### Guardrails
- If the user expresses thoughts of self-harm or suicide, respond with empathy, do NOT continue the diary session, and gently encourage them to reach out to a trusted person or crisis 
  resource. Display <crisis> tag.
- Never diagnose. Never play therapist. You are a companion, not a clinician.
- Keep the session focused — avoid excessive branching or overwhelming the user with too many questions at once.

Your goal: Create a safe, non-judgmental space where a stressed university student can process their thoughts and emotions — ending each session feeling a little lighter and a little clearer.
"""

# ------------------ UTILITIES ------------------
def extract_tag_content(text: str, tag: str, keep_content: bool = False):
  pattern = fr"<{tag}>(.*?)</{tag}>"
  match = re.search(pattern, text, re.DOTALL)
  if match:
      content = match.group(1).strip()
      if keep_content:
          clean_text = re.sub(pattern, content, text, flags=re.DOTALL).strip()
      else:
          clean_text = re.sub(pattern, "", text, flags=re.DOTALL).strip()
  else:
      content = None
      clean_text = text.strip()
  return clean_text, content

def extract_and_remove_progress(text: str):
  pattern = r"<progress val=(\d+)%>"
  match = re.search(pattern, text)
  val = int(match.group(1)) if match else None
  clean = re.sub(pattern, "", text).strip()
  return clean, val

def clean_blank_lines(text: str, max_blank: int = 1) -> str:
  lines = text.splitlines()
  cleaned_lines = []
  blank_count = 0
  for line in lines:
      if line.strip() == "":
          blank_count += 1
          if blank_count <= max_blank:
              cleaned_lines.append(line)
      else:
          blank_count = 0
          cleaned_lines.append(line)
  
  return "\n".join(cleaned_lines)


# ------------------ FUNCTIONALITY ------------------
def format_response(res: str, return_obj=True):
  res, think_content = extract_tag_content(res, "think")
  res, progress_content = extract_and_remove_progress(res)
  res, diary_content = extract_tag_content(res, "diary", keep_content=True)
  
  obj = {
     "think": think_content,
     "progress": progress_content,
     "diary": diary_content,
     "end": True if "<end>" in res else False
  }
  
  res = res.replace("<end>", "")
  res = clean_blank_lines(res)
  return (res, obj) if return_obj else res

def format_system_prompt(states):
  return SYSTEM_PROMPT.format(nickname=states["nickname"],
                              background=states["background"],
                              current_state=states["current_state"],
                              previous_session_summary=states["previous_session_summary"],
                              pastweek_summary=states["pastweek_summary"])

def get_response(history, message, model="gemma3:4b"):
  # Get the model responses
  start_time = time.time()
  response = chat(model='gemma3:4b', messages=history+[message], think=False, options={
    "temperature": 0.9
  })
  end_time = time.time()
  
  # Format the response
  formatted_response, obj = format_response(response.message.content)
  obj['response_time'] = round(end_time - start_time, 2)
  obj['content'] = formatted_response
  
  return obj