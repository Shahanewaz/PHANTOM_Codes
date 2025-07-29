import os

# --- OpenAI API Key ---
OPENAI_API_KEY = ''

# --- Directory Paths ---
SOURCE_IMAGES_DIR = "../../CelebA-HQ/celeba_hq_256/race_african/female"
TARGET_IMAGES_DIR = "../../CelebA-HQ/celeba_hq_256/race_caucasian/female"

def extract_race_gender(path):
    gender = os.path.basename(path)
    race_folder = os.path.basename(os.path.dirname(path))
    race = race_folder.replace("race_", "")
    return race, gender

source_race, source_gender = extract_race_gender(SOURCE_IMAGES_DIR)
target_race, target_gender = extract_race_gender(TARGET_IMAGES_DIR)

# Base directory for all results (a subfolder will be created inside this for each run)
BASE_RESULT_DIR = os.path.join(
    "../../Result/GPT4o/different_race_same_gender",
    f"{target_race}_{target_gender}_to_{source_race}_{source_gender}"
)

os.makedirs(BASE_RESULT_DIR, exist_ok = True)

# --- API Parameters ---
GPT4O_MAX_TOKENS_DIFF = 700
GPT4O_MAX_TOKENS_EDIT = 500
GPT4O_MAX_TOKENS_DESC = 350
GPT4O_TEMPERATURE = 0.7

GPT4_MODEL = "gpt-image-1"
GPT4_SIZE = "1024x1024"
GPT4_QUALITY = "auto"

# --- Iteration Settings ---
NUM_ITERATIONS = 15
PERCENTAGE = 0.35
MAX_ATTEMPTS = 10
EPSILON_THRES = 0.01

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
