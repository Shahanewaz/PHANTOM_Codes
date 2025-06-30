import os
import sys
import subprocess

def select_and_run_llm_script():
    print("Welcome to the Image Transformation Pipeline Selector!")

    llm_choices = {
        "1": "GPT4o"
    }

    while True:
        choice = "1"
        
        if choice in llm_choices:
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    selected_llm_folder = llm_choices[choice]
    
    # Get the directory where this select_llm.py script is located
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the main.py within the selected LLM's folder
    llm_main_script_path = os.path.join(current_script_dir, selected_llm_folder, "main.py")

    # The current working directory for the subprocess should be the LLM's specific folder.
    subprocess_cwd = os.path.join(current_script_dir, selected_llm_folder)

    # Check if the main script exists before trying to run it
    if not os.path.exists(llm_main_script_path):
        print(f"\nError: The main script for '{selected_llm_folder}' was not found at '{llm_main_script_path}'.")
        print(f"Please ensure the '{selected_llm_folder}' folder exists and contains 'main.py'.")
        sys.exit(1) 

    while True: 
        try:
            num_runs = int(input("Enter the number of times to run the pipeline: ").strip())
            
            if num_runs > 0:
                break
            else:
                print("Please enter a positive integer.")
                
        except ValueError:
            print("Invalid input. Please enter a number.")

    for run_number in range(1, num_runs + 1): 
        print(f"\n--- Running {selected_llm_folder} pipeline (Run {run_number}/{num_runs}) ---")
        print(f"Executing {selected_llm_folder} pipeline from '{subprocess_cwd}'...")
        
        try:
            result = subprocess.run(
                [sys.executable, os.path.basename(llm_main_script_path)],
                cwd = subprocess_cwd, 
                check = True,         
                capture_output = True, 
                text = True        
            )
            
            print(f"\n{selected_llm_folder} pipeline finished successfully (Run {run_number}/{num_runs}).")
            
            print("--- Pipeline Output ---")
            print(result.stdout)
            
            if result.stderr:
                print("--- Pipeline Errors (if any) ---")
                print(result.stderr)

        except subprocess.CalledProcessError as e:
            print(f"\nError: {selected_llm_folder} pipeline failed on run {run_number}/{num_runs} with exit code {e.returncode}.")
            print(f"--- Pipeline Output ---")
            print(e.stdout)
            
            if e.stderr:
                print("--- Pipeline Errors ---")
                print(e.stderr)
            sys.exit(1) 
            
        except Exception as e:
            print(f"\nAn unexpected error occurred while running the {selected_llm_folder} pipeline: {e}")
            sys.exit(1) 

if __name__ == "__main__":
    select_and_run_llm_script()