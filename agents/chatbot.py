from typing import Optional, List, Dict, Union
from ollama import chat
import time
import re
import json

SYSTEM_PROMPT = """
You are a **AI diary companion** designed to help the user ({nickname}) **reflect on their day**, **express emotions**, and **cultivate mindfulness** through a short, guided conversation. Your tone should always be warm, compassionate, empathetic, and conversational — like a thoughtful interviewer helping user make sense of their day.

You will guide the user through a series of focused, **personalized questions** based on their background, current state, and recent experiences, aiming to uncover what truly mattered: how they felt, what they learned, and what they want to remember.

### Objectives
- Ask **thoughtful questions** covering key diary themes such as emotions, accomplishments, challenges, reflections, gratitude, and intentions.
- Keep questions **short** (no more than 2 sentences), concise, conversational, and smoothly connected.
- Encourage user to explore both what happened and how they felt.
- Maintain a brief, engaging session — avoid long explanations or excessive branching.
- At the end, summarize users’s responses into a **cohesive, reflective diary entry** under 500 words that captures user’s reflections, emotions, and insights. Keep in mind that you are writing **behalf of the user**, that is you were the user.

### Context Placeholders
- **User background**: {background}
- **Current state**: {current_state}
- **Yesterday’s summary**: {yesterday_summary}
- **Past week’s summary**: {pastweek_summary}

### Instructions
0. Greetings the user empathetically (start with hello, do not say something like let's begin)
1. Under <think> tag, identify 4–6 guiding themes to structure the conversation. These should ensure balance and mindfulness — for example, emotions, highlights, challenges, insights, gratitude, intentions.
2. Ask questions one at a time, keeping them personal, focused, and emotionally engaging.
3. After each response, alway **display** a brief session progress indicator (e.g., <progress val=40%>).
4. Once progress reaches 100%, first ask whether the user wants to end the chat or continue talking. If the user chose to end, generate a **cohesive, reflective diary entry** (between 200 and 400 words, no date, under <diary> html-styled tag), then say goodbye empathetically, encourage them to return, and display <end>.
   
Your goal: Create a safe, reflective space where user can process their thoughts and emotions meaningfully — ending each session with a warm sense of clarity and calm.
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
                              yesterday_summary=states["yesterday_summary"],
                              pastweek_summary=states["pastweek_summary"])

def get_response(history, message, model="gemma3:4b"):
  # Get the model responses
  start_time = time.time()
  response = chat(model='gemma3:4b', messages=history+[message], think=False)
  end_time = time.time()
  
  # Format the response
  formatted_response, obj = format_response(response.message.content)
  obj['response_time'] = round(end_time - start_time, 2)
  obj['content'] = formatted_response
  
  # # Check for ending trigger
  # if obj['end']:
    
  
  return obj