import os

# --- OpenAI API Key ---
OPENAI_API_KEY = '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'

# --- Directory Paths ---
# Directory containing source images (e.g., CelebA-HQ)
SOURCE_IMAGES_DIR = "../../CelebA-HQ/celeba_hq_256"

# Base directory for all results (a subfolder will be created inside this for each run)
BASE_RESULT_DIR = "../../Result/GPT4o"

# --- API Parameters ---
GPT4O_MAX_TOKENS_DIFF = 700
GPT4O_MAX_TOKENS_EDIT = 500
GPT4O_MAX_TOKENS_DESC = 350
GPT4O_TEMPERATURE = 0.7

GPT4_MODEL = "gpt-image-1"
GPT4_SIZE = "1024x1024"
GPT4_QUALITY = "auto"

# --- Iteration Settings ---
NUM_ITERATIONS = 10 

# --- Conditional Exit Keywords ---
UNSUCCESSFUL_KEYWORDS = [
    "unable to process",
    "can't process",
    "cannot process",
    "failed to process",
    "did not process",
    "error",
    "something went wrong",
    "no visual differences could be determined",
]