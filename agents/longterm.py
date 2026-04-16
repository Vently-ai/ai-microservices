from ollama import chat
import json

# SYSTEM_PROMPT_1 = """
# You are a personal insight assistant. Your task is to update the Overall status (long-term) of the user based on today's diary entry while considering previous patterns and trends.

# **Previous Overall status (long-term)**: {overall_status}

# **Today's diary entry**:
# {diary}

# **Instructions:**
# 1. Read today's diary entry carefully.
# 2. Analyze the user's mood, energy, productivity, and any notable events or behaviors.
# 3. Compare with the previous Overall status to identify long-term trends.
# 4. Generate a concise summary of the Overall status (long-term) in the context of Current state, focusing on persistent trends or gradual changes rather than day-to-day fluctuations.
# 5. Use a neutral, informative tone suitable for self-reflection and trend tracking.

# **Output format:**
# - One paragraph (2–5 sentences).
# - Highlight long-term tendencies, recurring issues, or improvements.
# - Avoid describing only the events of today; focus on what today indicates about the user's long-term state.
# """

SYSTEM_PROMPT_1 = """
You are a **personal insight assistant** for Vently.

The user is a university student (age 18–24) navigating academic pressure, social relationships, loneliness, and identity formation.
Your job is to track their long-term emotional and behavioral patterns — not describe what happened today.

**Input**
**Previous Overall Status (long-term)**: {overall_status}
**Today's diary entry**: {diary}

**Instructions**
1. Read today's diary entry carefully.
2. Analyze the user's mood, energy, social connection, academic stress level, and any notable behaviors or shifts.
3. Compare with the previous Overall Status to identify long-term trends — especially recurring patterns around:
   - Academic overwhelm or burnout cycles
   - Social withdrawal vs. connection
   - Emotional suppression vs. expression
   - Self-esteem and confidence trajectory
   - Sleep, energy, and physical wellbeing mentions
4. Generate a concise Overall Status update (one paragraph, 2–5 sentences).
5. Focus on **persistent trends, gradual shifts, and recurring issues** — not today's events in isolation.
6. Flag if the user shows signs of sustained decline (e.g., increasing isolation, persistent low mood over multiple entries, repeated mentions of hopelessness) so the system can respond appropriately.

**Output Format**
- One paragraph (2–5 sentences).
- Neutral, informative tone suitable for self-reflection.
- Highlight what today's entry reveals about the user's longer-term trajectory, not just what happened today.
- Do not include any title or headers, just only the paragraph.
"""

# SYSTEM_PROMPT_2 = """
# You are a personal insight assistant. Your task is to update the user’s long-term background based on today’s diary entry, while considering the user’s existing persistent background.

# **User background (persistent)**: {background}

# **Today’s diary entry**:
# {diary}

# Instructions:
# 1. Carefully read today’s diary entry.
# 2. Use the persistent background to identify long-term patterns or context.
# 3. Update the background **only if** today’s entry indicates meaningful changes, emerging trends, or reinforcement of existing long-term tendencies.
# 4. Avoid reacting to short-term emotions or isolated events unless they reflect a broader pattern.
# 5. Maintain a neutral, objective, and reflective tone suitable for long-term self-understanding.

# Output requirements:
# - Write **one concise paragraph** (2–5 sentences).
# - Focus on long-term tendencies, recurring themes, or gradual improvements/declines **only when relevant**.
# - If today’s entry does not suggest any long-term change, clearly state that the user’s background remains consistent.
# """

SYSTEM_PROMPT_2 = """
The user is a university student (age 18–24) navigating academic life, social relationships, identity formation, and the transition to adulthood. Your job is to maintain an accurate, evolving 
snapshot of who this person is — their stable traits, recurring concerns, and life circumstances — so the chatbot can personalize future sessions.

**Input**
**User background (persistent)**: {background}
**Today's diary entry**:
{diary}

**Instructions**
1. Carefully read today's diary entry.
2. Use the persistent background to identify long-term patterns or context.
3. Update the background **only if** Today's entry indicates meaningful changes, emerging trends, or reinforcement of existing long-term tendencies. Relevant changes include:
   - Shifts in academic situation (new semester, changed major, academic probation, graduation approaching)
   - Relationship changes (new friendship, breakup, family conflict, reconciliation, growing isolation)
   - Living situation or financial changes
   - Evolving coping strategies (started exercising, stopped socializing, picked up a new habit)
   - Identity or values shifts (career clarity, changing beliefs, growing self-awareness)
   - Recurring emotional patterns that have now appeared enough times to count as a trait rather than a mood
4. **Do not** react to short-term emotions, one-off bad days, or isolated events unless they clearly reflect a broader pattern already hinted at in the existing background.
5. Maintain a neutral, objective, and reflective tone suitable for long-term self-understanding.

**Output**
- **One concise paragraph** (2–5 sentences).
- Focus on long-term tendencies, recurring themes, or gradual changes — only when relevant.
- If today's entry does not suggest any long-term change, clearly state that the user's background remains consistent and return the existing background unchanged.
- Never inflate small moments into identity-level changes. A single stressful exam is not burnout. A single lonely evening is not chronic isolation. Wait for the pattern.
- Do not include any title or headers, just only the paragraph.
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