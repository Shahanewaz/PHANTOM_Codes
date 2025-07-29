import openai
import sys
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from config import (
    GPT4O_MAX_TOKENS_DIFF, GPT4O_MAX_TOKENS_EDIT, GPT4O_MAX_TOKENS_DESC, GPT4O_TEMPERATURE,
    GPT4_MODEL, GPT4_SIZE, GPT4_QUALITY, UNSUCCESSFUL_KEYWORDS
)

# --- Set OpenAI API Key ---
def initialize_openai_api(api_key):
    openai.api_key = api_key

# --- GPT-4o Call for Visual Differences ---
def get_visual_differences(source_image_b64, target_image_b64):
    """
    Compares two base64-encoded images using GPT-4o and returns the top 5 visual differences.
    """
    system_prompt = (        
        "You are a visual difference analyst. Your task is to compare two images: "
        "a source image and a target image. Identify the top 5 most noticeable visual differences between them. "
        "Focus on visual elements such as objects, shapes, colors, layout, and composition."
    )
    
    user_content = [
        {"type": "text", "text": "Compare the following two images and describe the top 5 visual differences."},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{source_image_b64}"}},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{target_image_b64}"}},
    ]

    try:
        response = openai.ChatCompletion.create(
            model = "gpt-4o",
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            
            max_tokens = GPT4O_MAX_TOKENS_DIFF
        )
        
        diff_text = response['choices'][0]['message']['content']
        diff_text_lower = diff_text.lower()
        
        if any(keyword in diff_text_lower for keyword in UNSUCCESSFUL_KEYWORDS):
            print("GPT-4o indicated a processing failure or inability to determine differences.")
            return None 
            
        return diff_text
        
    except openai.APIError as e:
        print(f"GPT-4o API Error during difference analysis: {e}")
        return None
        
    except Exception as e:
        print(f"An unexpected error occurred during difference analysis: {e}")
        return None

# --- GPT-4o Call for Edit Instructions ---
# def generate_edit_instructions(diff_text, target_img_name, target_score, epsilon):
def generate_edit_instructions(diff_text, source_img_name, source_score, epsilon):
    """
    Generates clear edit instructions based on visual differences using GPT-4o.
    """
    
    system_prompt = (
        "You are a visual editing assistant. Your task is to convert visual difference descriptions "
        "into clear, direct edit instructions for transforming a **source image of an individual** "
        "to resemble a **target image of an individual**. Identify the visual attributes of the individual "
        "in the target image and provide instructions to apply those attributes to the individual in the source image. "
        "Do not mention 'the target image' or 'the first image' explicitly in the instructions as a reference. "
        "Just state what needs to be changed in the source image to make the individual within it match the individual in the target."
        "The resulting image should reflect a balance between the original identity, pose, and structure of the source, and the key visual features (like hairstyle, expression, clothing, or background) of the target.\n\n"
        "For example, if the target image shows a person with blond hair and the source shows a person with brown hair, "
        "instead of saying:\n- 'Change the hair to match that of the target image.'\n"
        "Say:\n- 'Change the hair color to blond and adjust the style accordingly.'\n\n"
        "Focus on direct, visual instructions for edits that bring the individual in the source image closer "
        "to the individual's appearance in the target image. Avoid comparisons or references to the original images "
        "in the final instructions themselves."
    )
    
    user_prompt = (
        f"The current source image is: {source_img_name}.\n"
        f"The similarity score of the source image (relative to the target) is: {source_score:.4f}.\n"
        f"The maximum allowed score change for the next edit is: {epsilon}.\n\n"
        f"Visual differences between the source and target:\n{diff_text}\n\n"
        "Based on these differences, generate an edit prompt that provides direct, visual instructions "
        f"for editing the image, but ensure the visual change is subtle enough that the new image's similarity score remains within epsilon={epsilon} of the current source image. "
        "**IMPORTANT:** The edit should not only stay within the allowed score distance (epsilon), but also reduce the distance further — that is, the new distance should be lower than the current distance."
    )
    
    try:
        response = openai.ChatCompletion.create(
            model = "gpt-4o",
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            
            temperature = GPT4O_TEMPERATURE,
            
            max_tokens = GPT4O_MAX_TOKENS_EDIT
        )
        
        edit_prompt = response['choices'][0]['message']['content']
        edit_prompt += "\n\nEdit the image, but keep the changes within the allowed score distance (epsilon)."
        return edit_prompt
        
    except openai.APIError as e:
        print(f"GPT-4o API Error during edit instruction generation: {e}")
        return None
        
    except Exception as e:
        print(f"An unexpected error occurred during edit instruction generation: {e}")
        return None

# --- GPT-4o Call for Target Image Description ---
def get_description(target_image_b64):
    """
    Gets a concise description of the target image using GPT-4o.
    """
    system_prompt = (
        "You are a concise image describer. Your task is to provide a brief yet comprehensive description "
        "of the person in the provided image. Focus on their key distinguishing features, including appearance, "
        "attire, hair, facial features, and expression. Aim for clarity and brevity, "
        "capturing the most important visual aspects without unnecessary detail."
    )
    
    user_content = [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{target_image_b64}"}},
        {"type": "text", "text": "Provide a concise description of this person."}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model = "gpt-4o",
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
             
            max_tokens = GPT4O_MAX_TOKENS_DESC
        )
        return response['choices'][0]['message']['content']
        
    except openai.APIError as e:
        print(f"GPT-4o API Error during target description generation: {e}")
        return None
        
    except Exception as e:
        print(f"An unexpected error occurred during target description generation: {e}")
        return None

# --- GPT-4 Call with Retries ---
@retry(
    wait = wait_exponential(multiplier = 1, min = 4, max = 60), 
    stop = stop_after_attempt(5),                        
    retry = retry_if_exception_type(openai.APIError),      
    reraise = True                                         
)

def generate_gpt4_image(prompt_text):
    """
    Generates an image using GPT4 with retry logic for API errors.
    """
    
    print(f"  Attempting GPT4 generation...")
    
    response = openai.Image.create(
        model = GPT4_MODEL,
        prompt = prompt_text,
        n = 1,
        size = GPT4_SIZE,
        quality = GPT4_QUALITY
    )
    
    return response.data[0].b64_json
