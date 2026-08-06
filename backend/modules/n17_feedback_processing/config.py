GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS = {
    "gpt_120b": "openai/gpt-oss-120b",
    "groq_70b": "llama-3.3-70b-versatile",
    "qwen_32b": "qwen/qwen3-32b",
    "groq_8b": "llama-3.1-8b-instant",
    "gpt_20b": "openai/gpt-oss-20b",
    "gpt_safeguard": "openai/gpt-oss-safeguard-20b",
    "groq_scout": "meta-llama/llama-4-scout-17b-16e-instruct",
}
LLM_CHAIN = "groq_70b,qwen_32b,groq_8b,groq_scout"
USER_AGENT = "travel-exp-planner-n17/1.0"
MAX_RETRIES = 3
RETRY_WAIT_BASE = 2
LLM_TEMP = 0.1