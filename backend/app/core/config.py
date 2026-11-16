import os

# Mentor Edu AI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
AI_MODEL_FAST = os.getenv("AI_MODEL_FAST", "gpt-6-luna").strip()
AI_MODEL_SMART = os.getenv("AI_MODEL_SMART", "gpt-6.1-sol").strip()
