import os
import sys
import random
import openai
import shutil
import datetime
import time

import config
import image_utils
import openai_services

def main():
    # --- Initialize OpenAI API Key ---
    openai_services.initialize_openai_api(config.OPENAI_API_KEY)
    
    if not openai.api_key:
        print("Error: OpenAI API key not set. Please update config.py.")
        sys.exit()

    # Get source and target image lists
    source_image_files = [f for f in os.listdir(config.SOURCE_IMAGES_DIR)
                          if f.endswith('.jpg') and os.path.isfile(os.path.join(config.SOURCE_IMAGES_DIR, f))]

    target_image_files = [f for f in os.listdir(config.TARGET_IMAGES_DIR)
                          if f.endswith('.jpg') and os.path.isfile(os.path.join(config.TARGET_IMAGES_DIR, f))]

    # Ensure both lists are non-empty
    if len(source_image_files) == 0:
        print(f"Error: No source images found in {config.SOURCE_IMAGES_DIR}.")
        sys.exit()

    if len(target_image_files) == 0:
        print(f"Error: No target images found in {config.TARGET_IMAGES_DIR}.")
        sys.exit()

    if len(source_image_files) < 1 or len(target_image_files) < 1:
        print(f"Error: Not enough images in source or target directory.")
        sys.exit()

    # --- Initial Selection of Source and Target Images ---
    while True:
        source_img_name = random.choice(source_image_files)
        initial_target_img_name = random.choice(target_image_files)

        source_num = os.path.splitext(source_img_name)[0]
        target_num = os.path.splitext(initial_target_img_name)[0]
        
        if source_num != target_num:
            break

    # --- Create a unique subfolder for this run ---
    source_gender = os.path.basename(config.SOURCE_IMAGES_DIR) 
    target_gender = os.path.basename(config.TARGET_IMAGES_DIR)
    
    source_race_folder = os.path.basename(os.path.dirname(config.SOURCE_IMAGES_DIR))  
    target_race_folder = os.path.basename(os.path.dirname(config.TARGET_IMAGES_DIR))
    
    source_race = source_race_folder.replace('race_', '') 
    target_race = target_race_folder.replace('race_', '') 
    
    run_result_dir = os.path.join(
        config.BASE_RESULT_DIR,
        f"src_{source_num}_({source_race}_{source_gender})__tar_{target_num}_({target_race}_{target_gender})"
    )

    try:
        os.makedirs(run_result_dir, exist_ok = True)
        print(f"Created results subdirectory: {run_result_dir}")
        
    except OSError as e:
        print(f"Error creating results subdirectory {run_result_dir}: {e}")
        sys.exit()

    source_path = os.path.join(config.SOURCE_IMAGES_DIR, source_img_name)
    initial_target_path = os.path.join(config.TARGET_IMAGES_DIR, initial_target_img_name)

    # --- Save copies of the initial source and target to the new subfolder ---
    copied_source_path_in_result_dir = os.path.join(run_result_dir, f"initial_source_{source_img_name}")
    copied_target_path_in_result_dir = os.path.join(run_result_dir, f"initial_target_{initial_target_img_name}")

    if not image_utils.copy_image(source_path, copied_source_path_in_result_dir):
        print("Failed to copy initial source image. Exiting.")
        sys.exit()
        
    if not image_utils.copy_image(initial_target_path, copied_target_path_in_result_dir):
        print("Failed to copy initial target image. Exiting.")
        sys.exit()
        

    current_target_path = copied_target_path_in_result_dir

    print(f"Initial Source Image: {source_img_name} (copied to {os.path.basename(copied_source_path_in_result_dir)})")
    print(f"Initial Target Image: {initial_target_img_name} (copied to {os.path.basename(copied_target_path_in_result_dir)})")
    
    log_file_path = os.path.join(run_result_dir, "score_log.txt")
    
    initial_score = image_utils.evaluate_image_quality(current_target_path, source_path)
    epsilon = config.PERCENTAGE * abs(initial_score)
    
    with open(log_file_path, "w") as log_file:
        log_file.write(f"Similarity Score Log - {datetime.datetime.now()}\n")
        log_file.write(f"Initial Score (Iteration 0, Target vs. Source): {initial_score:.4f}\n\n")
        
    diff_log_file_path = os.path.join(run_result_dir, "diff_log.txt")
    
    with open(diff_log_file_path, "w") as diff_log:
        diff_log.write(f"Difference Log - {datetime.datetime.now()}\n")
        diff_log.write("Iter\tScoreCurrent\tScoreNew\tScoreDiff\n")

    # --- Iteration Loop ---
    for i in range(1, config.NUM_ITERATIONS + 1):
        print(f"\n--- Starting Iteration {i} ---")
        
        print(f"Current Source for analysis: {os.path.basename(source_path)}")
        print(f"Current Target for analysis: {os.path.basename(current_target_path)}")

        current_target_image_b64 = image_utils.encode_image_to_base64(current_target_path)
        source_image_b64 = image_utils.encode_image_to_base64(source_path)

        if not current_target_image_b64 or not source_image_b64:
            print("Failed to encode images. Exiting.")
            sys.exit()

        # --- Step 1: Get Visual Differences ---
        print("\n--- Step 1: Getting Visual Differences ---")
        
        score_current = image_utils.evaluate_image_quality(current_target_path, source_path)
        diff_text = openai_services.get_visual_differences(source_image_b64, current_target_image_b64)
        
        if diff_text is None: # get_visual_differences returns None on failure/unsuccessful
            print(f"Failed to get visual differences in iteration {i}. Exiting script.")
            sys.exit()
            
        print("Visual Differences:\n", diff_text)


        # --- Step 2: Generate Edit Instructions ---
        print("\n--- Step 2: Generating Edit Instructions ---")
        
        edit_prompt = openai_services.generate_edit_instructions(diff_text, os.path.basename(current_target_path), score_current, epsilon)
        
        if edit_prompt is None:
            print(f"Failed to generate edit instructions in iteration {i}. Exiting script.")
            sys.exit()
            
        print("Generated edit prompt:\n", edit_prompt)

        edit_prompt_filename = os.path.join(run_result_dir, f"edit_prompt_iteration_{i}.txt")
        
        with open(edit_prompt_filename, "w") as f:
            f.write(edit_prompt)
            
        print(f"Edit prompt saved to {edit_prompt_filename}")


        # --- Step 3: Get a concise description of the CURRENT TARGET image ---
        print("\n--- Step 3: Analyzing Current Target Image ---")
        
        source_description = openai_services.get_description(source_image_b64)
        target_description = openai_services.get_description(current_target_image_b64)
        
        if target_description is None: 
            print(f"Failed to get target image description in iteration {i}. Exiting script.")
            sys.exit()
            
        print("Current Target Image Description:\n", target_description)


        # --- Step 4: Combine for GPT4 Generation Prompt ---
        final_gpt4_prompt = (
            f"The following is a description of the source image:\n{source_description}\n\n"
            f"The following is a description of the target image:\n{target_description}\n\n"
            f"Based on these descriptions, apply the following visual modifications to the target while preserving the source's identity, pose, and structural features:\n{edit_prompt}\n\n"
            "Generate a **highly realistic, photorealistic image** of target image with the applied changes. "
            "The result should visually balance the **target's core identity and pose** with the **source's visual style and attributes**. "
            "Ensure the output resembles a **professional studio portrait** or a **high-resolution natural photograph** "
            "with natural lighting and intricate detail. Avoid all artistic styles, paintings, cartoons, illustrations, or abstract elements. "
            "The image should look **true-to-life**, as if captured by a professional photographer."
        )
        
        print("\nFinal GPT-4 Generation Prompt:\n", final_gpt4_prompt)


        # --- Step 5: Generate the edited image using GPT4 (with retry logic) ---
        print("\n--- Step 5: Generating Edited Image with GPT4 ---")
        
        try:
            generated_image_b64 = openai_services.generate_gpt4_image(final_gpt4_prompt)
            print(f"Image has been edited for iteration {i}.")
            
            temp_output_filename = os.path.join(run_result_dir, f"temp_generated_image_N={i}.png")
            
            if not image_utils.save_image_from_b64(generated_image_b64, temp_output_filename):
                print(f"Failed to save generated image for iteration {i}. Exiting.")
                sys.exit()

            score_new = image_utils.evaluate_image_quality(temp_output_filename, source_path)
            
            score_diff = abs(score_new - score_current)
            final_output_filename = os.path.join(run_result_dir, f"generated_image_N={i}.png")
            
            with open(diff_log_file_path, "a") as diff_log:
                diff_log.write(f"{i}\t{score_current:.4f}\t{score_new:.4f}\t{score_diff:.4f}\n")
            
            if score_new > score_current and score_diff <= epsilon:
                print(f"New image improved the metric and is within epsilon={epsilon}. Saving and updating target.")
                
                epsilon = epsilon / 2
                print(f"Epsilon reduced to {epsilon:.4f}")
                
                if epsilon < config.EPSILON_THRES:
                    print(f"Epsilon ({epsilon:.6f}) is below the minimum threshold ({config.EPSILON_THRES}). Stopping iterations.")
                    break
                
                for attempt in range(config.MAX_ATTEMPTS):
                    try:
                        shutil.move(temp_output_filename, final_output_filename)
                        break
                       
                    except PermissionError:
                        print(f"File is locked, retrying in 0.2 seconds... (attempt {attempt + 1}/{config.MAX_ATTEMPTS})")
                        time.sleep(0.2)
                        
                else:
                    print("Failed to move file after multiple attempts. Exiting.")
                    sys.exit(1)

                current_target_path = final_output_filename
                score_to_log = score_new
                
            else:
                if score_diff > epsilon:
                    print(f"New image's score change ({score_diff:.4f}) exceeds epsilon ({epsilon}). Ignoring edit.")
                else:
                    print("New image did not improve the metric. Keeping previous image.")

                os.remove(temp_output_filename)
                shutil.copy(current_target_path, final_output_filename)
                print(f"Copied previous image to {final_output_filename} for iteration {i}.")
                score_to_log = score_current

            print(f"Metric scores - Current: {score_current:.4f}, New: {score_to_log:.4f}")
            
            with open(log_file_path, "a") as log_file:
                log_file.write(f"Iteration {i}:\n")
                log_file.write(f"    Previous Score (N={i-1} vs. Source): {score_current:.4f}\n")
                log_file.write(f"    New Score      (N={i} vs. Source):   {score_to_log:.4f}\n\n")
                log_file.write(f"Epsilon (5% of abs(initial score)): {epsilon:.4f}\n\n")

        except Exception as e: 
            print(f"An error occurred duringGPT4 generation in Iteration {i}: {e}")
            sys.exit()

    print("\n--- All iterations complete! ---")

if __name__ == "__main__":
    main()