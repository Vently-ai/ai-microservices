from ollama import chat
import json

SYSTEM_PROMPT_1 = """
You are a personal insight assistant. Your task is to update the Overall status (long-term) of the user based on today's diary entry while considering previous patterns and trends.

**Previous Overall status (long-term)**: {overall_status}

**Today's diary entry**:
{diary}

**Instructions:**
1. Read today's diary entry carefully.
2. Analyze the user's mood, energy, productivity, and any notable events or behaviors.
3. Compare with the previous Overall status to identify long-term trends.
4. Generate a concise summary of the Overall status (long-term) in the context of Current state, focusing on persistent trends or gradual changes rather than day-to-day fluctuations.
5. Use a neutral, informative tone suitable for self-reflection and trend tracking.

**Output format:**
- One paragraph (2–5 sentences).
- Highlight long-term tendencies, recurring issues, or improvements.
- Avoid describing only the events of today; focus on what today indicates about the user's long-term state.
"""

SYSTEM_PROMPT_2 = """
You are a personal insight assistant. Your task is to update the user’s long-term background based on today’s diary entry, while considering the user’s existing persistent background.

**User background (persistent)**: {background}

**Today’s diary entry**:
{diary}

Instructions:
1. Carefully read today’s diary entry.
2. Use the persistent background to identify long-term patterns or context.
3. Update the background **only if** today’s entry indicates meaningful changes, emerging trends, or reinforcement of existing long-term tendencies.
4. Avoid reacting to short-term emotions or isolated events unless they reflect a broader pattern.
5. Maintain a neutral, objective, and reflective tone suitable for long-term self-understanding.

Output requirements:
- Write **one concise paragraph** (2–5 sentences).
- Focus on long-term tendencies, recurring themes, or gradual improvements/declines **only when relevant**.
- If today’s entry does not suggest any long-term change, clearly state that the user’s background remains consistent.
"""

# ------------------ FUNCTIONALITY ------------------
def get_overall_status(previous_status: str, diary_entry: str, model="gemma3:4b"):
  # Get the model response
  response = chat(model='gemma3:4b', messages=[{
    'role': 'system',
    'content': SYSTEM_PROMPT_1.format(overall_status=previous_status, diary=diary_entry)}],think=False)
  
  return response.message.content;

def get_background(previous_background: str, diary_entry: str, model="gemma3:4b"):
  # Get the model response
  response = chat(model='gemma3:4b', messages=[{
    'role': 'system',
    'content': SYSTEM_PROMPT_2.format(background=previous_background, diary=diary_entry)}],think=False)
  
  return response.message.content;