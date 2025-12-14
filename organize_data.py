import os
import json
import shutil

# --- Configuration ---
# Set the base directory to the location of 'train_data'
BASE_DIR = 'UIT_HWDB_line/test_data'
OUTPUT_LABEL_FILE = 'label.json'
# --- End Configuration ---
# Initialize a dictionary to hold all combined label data
combined_labels = {}

print(f"Starting file processing in directory: {BASE_DIR}")

# 1. Combine all label.json files
# Iterate over all items (folders/files) directly under BASE_DIR
for item in os.listdir(BASE_DIR):
    # 'item' will be the folder name, e.g., '236'
    subdir_name = item
    subdir_path = os.path.join(BASE_DIR, subdir_name)

    # Check if the item is a numbered directory (like '1', '2', etc.)
    if os.path.isdir(subdir_path) and subdir_name.isdigit():
        print(f"Processing subdirectory: {subdir_name}/")
        
        label_file_path = os.path.join(subdir_path, OUTPUT_LABEL_FILE)
        
        if os.path.exists(label_file_path):
            print(f"  Found {OUTPUT_LABEL_FILE}. Combining data and renaming keys...")
            
            try:
                # FIX 1: Use 'encoding="utf-8"' to prevent charmap errors
                with open(label_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # --- KEY RENAMING LOGIC FOR LABELS ---
                renamed_data = {}
                for old_key, value in data.items():
                    # Create the new unique key: "folderName_originalFileName" (e.g., "236_1.jpg")
                    new_key = f"{subdir_name}_{old_key}"
                    renamed_data[new_key] = value
                
                # Update the combined_labels dictionary with the renamed keys
                combined_labels.update(renamed_data)
                
            except json.JSONDecodeError as e:
                print(f"  ❌ ERROR: Could not decode JSON in {label_file_path}. Skipping. Error: {e}")
            except Exception as e:
                print(f"  ❌ UNEXPECTED ERROR while reading {label_file_path}: {e}")
        else:
            print(f"  No {OUTPUT_LABEL_FILE} found. Skipping label combination for this folder.")

# 2. Write the combined labels to a single file in the BASE_DIR
final_label_path = os.path.join(BASE_DIR, OUTPUT_LABEL_FILE)
print(f"\nWriting combined labels to {final_label_path}...")

try:
    # FIX 2: Use 'encoding="utf-8"' and ensure_ascii=False for clean writing
    with open(final_label_path, 'w', encoding='utf-8') as f:
        json.dump(combined_labels, f, indent=4, ensure_ascii=False)
    print("✅ Successfully created/overwrote the final label.json.")
except Exception as e:
    print(f"❌ Failed to write the final label.json: {e}")

# 3. Move and rename all image files and remove the numbered subdirectories
print("\nMoving, renaming image files, and cleaning up subdirectories...")

# Re-iterate over the directories to move the images and clean up
for item in os.listdir(BASE_DIR):
    subdir_name = item
    subdir_path = os.path.join(BASE_DIR, subdir_name)

    if os.path.isdir(subdir_path) and subdir_name.isdigit():
        print(f"Processing directory for cleanup: {subdir_name}/")
        
        # Move all files (presumably images) from the subdirectory to BASE_DIR
        for filename in os.listdir(subdir_path):
            
            if filename == OUTPUT_LABEL_FILE:
                continue

            # --- IMAGE RENAMING LOGIC ---
            # Create the new unique filename: "folderName_originalFileName"
            new_filename = f"{subdir_name}_{filename}"
            
            # Construct full paths for source and destination
            source_path = os.path.join(subdir_path, filename)
            destination_path = os.path.join(BASE_DIR, new_filename)
            
            # Use shutil.move to move and rename the file
            try:
                if not os.path.exists(destination_path):
                    shutil.move(source_path, destination_path)
                    # print(f"  Moved and Renamed: {filename} -> {new_filename}") # Uncomment for verbose
                else:
                    print(f"  ⚠️ Skipping move: {new_filename} already exists in {BASE_DIR}. Data may be duplicated.")
            except Exception as e:
                print(f"  ❌ ERROR: Could not move {filename}. Skipping. Error: {e}")

        # After moving the contents, remove the now empty subdirectory
        try:
            os.rmdir(subdir_path)
            print(f"  ✅ Successfully removed empty directory: {subdir_name}/")
        except OSError as e:
            print(f"  ❌ ERROR: Could not remove directory {subdir_name}/. It might not be empty. Error: {e}")

print("\n--- Script finished ---")
print(f"Final files should now be in the '{BASE_DIR}' folder, with unique names (e.g., '236_1.jpg').")