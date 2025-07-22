
try:
    import os
    import sys

    verbose = os.environ['VSC_EDU_VERBOSE_PYTHON_LOGS']
    
    user_file_dir = os.environ['VSC_EDU_USER_FILE_DIR']
    os.chdir(user_file_dir)
    sys.path.append(user_file_dir)

    if verbose == "true":
        user_file_path = os.environ['VSC_EDU_FILE_TO_RUN']
        user_files_root = os.environ['VSC_EDU_USER_DIR_ROOT']
        
        print(f"Changed directory to {user_file_dir}")
        print(f"Running pedal user file: {user_file_path}")
        print(f"User files root: {user_files_root}")

except Exception as e:
    print("Error: Could not change directory to user file directory")
    print(e)
    pass
