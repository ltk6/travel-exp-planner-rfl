GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS = {
    "groq_qwen3_6": "qwen/qwen3.6-27b",
    "groq_qwen3_8": "qwen/qwen3.8-27b",
    "groq_gpt_oss_120b": "openai/gpt-oss-120b",
    "groq_gpt_oss_20b": "openai/gpt-oss-20b",
}
LLM_CHAIN = "groq_qwen3_6,groq_qwen3_8,groq_gpt_oss_120b,groq_gpt_oss_20b"
USER_AGENT = "travel-exp-planner-n5/1.0"

TARGET_ACT_COUNT = 10
MAX_RETRIES = 3
RETRY_WAIT_BASE = 2
LLM_TEMP = 0.1

