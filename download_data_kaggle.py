import os
import zipfile
import glob

# --- ! IMPORTANT: SECURITY WARNING ! ---
# Storing credentials in code is generally unsafe. Use this ONLY if you
# understand the risks. The safer approach is using the kaggle.json file.
# --- ! --- ! --- ! ---

# --- ! EDIT THESE LINES ! ---
KAGGLE_USERNAME = "your_username_here" # Your Kaggle username
KAGGLE_KEY = "your_api_key_here"       # Your Kaggle API Key (Token)
# --- ! --- ! --- ! ---


# Check if credentials have been updated from placeholders
if KAGGLE_USERNAME == "your_username_here" or KAGGLE_KEY == "your_api_key_here":
    # If not updated, we can't safely set the environment variables for import
    # The error message in the function will catch this, but we print an alert here
    # to maintain the original intent.
    pass
else:
    # Set environment variables immediately. This is the crucial step 
    # that prevents the OSError during the KaggleApi import below.
    os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME
    os.environ['KAGGLE_KEY'] = KAGGLE_KEY

# Import KaggleApi AFTER setting environment variables to prevent the OSError
from kaggle.api.kaggle_api_extended import KaggleApi


# Directory where all datasets will be downloaded
MAIN_DOWNLOAD_PATH = "Data"

# Name of the dataset that is needed
KAGGLE_DATASET_USERNAME = 'jamesvasanth'
KAGGLE_DATASET_NAME = 'adventure-works-dw-2008'

def download_my_datasets():
    """
    Authenticates with the Kaggle API using credentials hardcoded in the script, 
    finds all datasets for the specified user, downloads the full dataset ZIP, 
    and extracts all CSV files from it.
    """
    
    # Check if credentials have been updated from placeholders
    if KAGGLE_USERNAME == "your_username_here" or KAGGLE_KEY == "your_api_key_here":
        print("="*60)
        print("ERROR: Please edit the KAGGLE_USERNAME and KAGGLE_KEY variables")
        print("       in this script with your actual credentials.")
        print("="*60)
        return

    # 1. Initialize API.
    try:
        api = KaggleApi()
        api.authenticate() 
        print(f"Successfully authenticated as user: {KAGGLE_USERNAME}")
    except Exception as e:
        print("="*60)
        print("AUTHENTICATION FAILED.")
        print("Please double-check your KAGGLE_USERNAME and KAGGLE_KEY.")
        print(f"Details: {e}")
        print("="*60)
        return

    # 2. Create the main download directory if it doesn't exist
    os.makedirs(MAIN_DOWNLOAD_PATH, exist_ok=True)
    print(f"Downloads will be saved to: {os.path.abspath(MAIN_DOWNLOAD_PATH)}")

    # Initialize counters for better reporting
    total_datasets_processed = 0
    total_csvs_downloaded = 0
    total_datasets_skipped_by_error = 0

    # 3. Get list of all datasets owned by the user
    try:
        datasets = api.dataset_list(user=KAGGLE_DATASET_USERNAME)
        if not datasets:
            print(f"No datasets found for user '{KAGGLE_DATASET_USERNAME}'.")
            return
            
        print(f"\nFound {len(datasets)} total datasets. Starting full download process...")


    except Exception as e:
        print(f"Error listing datasets: {e}")
        print("An error occurred during the first API call. Check network or permissions.")
        return

    # 4. Loop through each dataset
    for i, dataset in enumerate(datasets):
        if dataset.ref == KAGGLE_DATASET_USERNAME + '/' + KAGGLE_DATASET_NAME:
            dataset_ref = dataset.ref
            dataset_slug = dataset_ref.split('/')[-1]
            
            print(f"\n--- Processing Dataset {i+1}/{len(datasets)}: {dataset_ref} ---")

            # Create a specific directory for this dataset's files
            dataset_download_dir = os.path.join(MAIN_DOWNLOAD_PATH)
            os.makedirs(dataset_download_dir, exist_ok=True)

            # The primary ZIP file name for the whole dataset
            dataset_zip_name = dataset_slug + ".zip"
            dataset_zip_path = os.path.join(dataset_download_dir, dataset_zip_name)

            try:
                total_datasets_processed += 1
                
                # 5. Download the entire dataset as a single ZIP file
                print(f"  -> Downloading full dataset ZIP to {dataset_zip_path}...")
                api.dataset_download_files(
                    dataset_ref,
                    path=dataset_download_dir,
                    quiet=True # Suppress download progress bar
                )
                
                if not os.path.exists(dataset_zip_path):
                    print(f"  -> ERROR: ZIP file was not created or download failed for {dataset_zip_name}. Skipping dataset.")
                    total_datasets_skipped_by_error += 1
                    continue

                # 6. Unzip the downloaded file (extracts all files)
                print("  -> Extracting all files...")
                with zipfile.ZipFile(dataset_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(dataset_download_dir)
                
                # 7. Clean up the zip file after extraction
                os.remove(dataset_zip_path)
                
                # 8. Count the extracted CSV files for accurate reporting
                # Use os.walk and glob to recursively find all CSV files
                extracted_csv_files = [
                    f for f in glob.glob(os.path.join(dataset_download_dir, '**', '*.csv'), recursive=True)
                ]
                
                current_csv_count = len(extracted_csv_files)
                total_csvs_downloaded += current_csv_count
                
                print(f"  -> Successfully extracted and counted {current_csv_count} CSV file(s).")
                if current_csv_count == 0:
                    print("  -> Warning: No CSV files were found after extraction.")

            except zipfile.BadZipFile:
                print(f"  -> ERROR: Failed to unzip {dataset_zip_name}. Skipping dataset.")
                total_datasets_skipped_by_error += 1
            except Exception as e:
                total_datasets_skipped_by_error += 1
                print(f"  -> ERROR processing dataset {dataset_ref}: {e}")
                print("  -> This can happen with private or script-based datasets. Skipping dataset.")
            
            # Ensure the downloaded zip is cleaned up even if there was a problem
            if os.path.exists(dataset_zip_path):
                os.remove(dataset_zip_path)


    print("\n" + "="*60)
    print("Download process complete.")
    print(f"Total datasets checked: {len(datasets)}")
    print(f"Total datasets skipped (API error or failure): {total_datasets_skipped_by_error}")
    print(f"Total CSV files successfully downloaded: {total_csvs_downloaded}")
    print(f"All files are in: {os.path.abspath(MAIN_DOWNLOAD_PATH)}")
    print("="*60)

if __name__ == "__main__":
    download_my_datasets()
