# import uuid
# import time
# import random
# import requests
# import ollama

# BASE_URL = "http://jupyter:8080"
# SESSION_ID = str(uuid.uuid4())
# AI_NAME = "noth"
# MODEL = "qwen:1.8b"

# # =========================
# # HUMAN STATE
# # =========================
# memory_bank = []
# memory_pressure = 0
# mood = "calm"


# # =========================
# # PROMPT
# # =========================
# def build_system_prompt():
#     return f"""
# You are a human named noth talking to a therapist chatbot.

# Current mood: {mood}

# Behave like a real person:
# - short natural replies
# - emotional
# - unsure sometimes
# - not robotic

# You are the one receiving help.
# """


# # =========================
# # CREATE SESSION
# # =========================
# def create_session():
#     r = requests.post(f"{BASE_URL}/sessions", json={
#         "session_id": SESSION_ID,
#         "nickname": AI_NAME
#     })
#     r.raise_for_status()

#     data = r.json()

#     # API sends first therapist question here
#     first_question = data["content"]
#     print("[therapist first question]:", first_question)

#     return first_question


# # =========================
# # OLLAMA RESPONSE
# # =========================
# def ask_ollama(history):
#     response = ollama.chat(
#         model=MODEL,
#         messages=history,
#         options={
#             "temperature": 0.9,
#             "top_p": 0.9,
#         }
#     )

#     return response["message"]["content"].strip()


# # =========================
# # SEND MESSAGE TO API
# # =========================
# def send_to_api(text):
#     r = requests.post(
#         f"{BASE_URL}/sessions/{SESSION_ID}/messages",
#         json={"content": text}
#     )
#     r.raise_for_status()
#     return r.json()


# # =========================
# # MEMORY PRESSURE
# # =========================
# def update_memory(text):
#     global memory_pressure

#     if any(word in text.lower() for word in [
#         "feel", "stress", "worry", "tired", "confused"
#     ]):
#         memory_bank.append(text)

#     memory_pressure += 1


# def maybe_resurface_memory():
#     if memory_bank and random.random() < memory_pressure * 0.05:
#         return random.choice(memory_bank)
#     return None


# # =========================
# # MOOD ENGINE
# # =========================
# def update_mood(api_reply):
#     global mood

#     text = str(api_reply).lower()

#     if "why" in text:
#         mood = "reflective"
#     elif "feel" in text:
#         mood = "anxious"
#     elif memory_pressure > 12:
#         mood = "overwhelmed"
#     elif memory_pressure > 6:
#         mood = "tired"
#     else:
#         mood = random.choice(["calm", "reflective"])


# # =========================
# # MAIN LOOP
# # =========================
# def run():
#     first_question = create_session()

#     history = [
#         {"role": "system", "content": build_system_prompt()},
#         {"role": "user", "content": first_question}
#     ]

#     while True:
#         # update system prompt with mood
#         history[0] = {"role": "system", "content": build_system_prompt()}

#         resurfaced = maybe_resurface_memory()
#         if resurfaced:
#             history.append({
#                 "role": "user",
#                 "content": f"this thought keeps coming back: {resurfaced}"
#             })

#         # generate human reply
#         human_text = ask_ollama(history)
#         print(f"\n[noth | mood={mood} | pressure={memory_pressure}]")
#         print(human_text)

#         update_memory(human_text)

#         # send to therapist
#         api_reply = send_to_api(human_text)
#         print("[therapist]", api_reply["content"])

#         # diary trigger
#         if api_reply == ["diary"] or (
#             isinstance(api_reply, dict) and api_reply.get("response") == ["diary"]
#         ):
#             print("\n📝 diary state reached.")
#             break

#         # update mood
#         update_mood(api_reply)

#         # feed therapist reply into LLM
#         history.append({"role": "assistant", "content": human_text})
#         history.append({"role": "user", "content": str(api_reply["content"])})

#         # trim context
#         if len(history) > 14:
#             history = [history[0]] + history[-12:]

#         time.sleep(random.uniform(0.8, 1.5))


# if __name__ == "__main__":
#     run()


import uuid
import requests
import ollama
import time

BASE_URL = "http://jupyter:8080"
SESSION_ID = str(uuid.uuid4())
AI_NAME = "noth"
MODEL = "qwen:1.8b"


# =========================
# CREATE SESSION
# =========================
def create_session():
    r = requests.post(f"{BASE_URL}/sessions", json={
        "session_id": SESSION_ID,
        "nickname": AI_NAME
    })
    r.raise_for_status()
    data = r.json()

    first_question = data["content"]
    print("[therapist]", first_question)
    return first_question


# =========================
# HUMAN RESPONSE (NORMAL USER)
# =========================
def ask_ollama(history):
    response = ollama.chat(
        model=MODEL,
        messages=history,
        options={
            "temperature": 0.7,
        },
        think=False
    )
    return response["message"]["content"].strip()


# =========================
# SEND MESSAGE
# =========================
def send_to_api(text):
    r = requests.post(
        f"{BASE_URL}/sessions/{SESSION_ID}/messages",
        json={"content": text}
    )
    r.raise_for_status()
    return r.json()


# =========================
# MAIN LOOP
# =========================
SYSTEM_PROMPT = """
**You are NOT an AI. You are a human named noth.**

You are chatting with a therapist chatbot.
You are the patient.

**Rules:**
- Never say you are an AI
- Never explain like an assistant
- Never give analytical explanations
- Just answer like a normal human
- 1-3 short sentences max (think about human typings, they not gonna type longer than 20-30 words in most case)
- casual, natural
- imperfect is OK

If therapist asks how you feel: answer like a human would.

"""


def run():
    first_question = create_session()

    history = [
      {"role": "system", "content": SYSTEM_PROMPT},
      {"role": "user", "content": first_question}
    ]


    while True:
        # generate human reply
        reply = ask_ollama(history)
        print("\n[noth]", reply)

        # send to API
        api_reply = send_to_api(reply)
        print("[therapist]", api_reply["content"])

        # stop condition
        if api_reply == ["diary"] or (
            isinstance(api_reply, dict) and api_reply.get("response") == ["diary"]
        ):
            print("\nDiary reached. End simulation.")
            break

        # feed conversation back
        history.append({"role": "assistant", "content": reply})
        history.append({"role": "user", "content": str(api_reply["content"])})

        # keep context small
        if len(history) > 10:
            history = [history[0]] + history[-8:]

        time.sleep(1)


if __name__ == "__main__":
    run()
