import os
from huggingface_hub import login, upload_folder
from dotenv import load_dotenv

# Load .env to see if you already have an HF_TOKEN
load_dotenv()

def upload_project():
    print("🚀 Preparing to upload NegotiationOpenEnv to Hugging Face Hub...")
    
    # Optional: If you have HF_TOKEN in your .env, it will use it
    token = os.getenv("HF_TOKEN")
    if token:
        login(token=token)
    else:
        print("No HF_TOKEN found in .env. Interactive login required.")
        login()

    # Define the repo ID
    repo_id = "AshuBharti/NegotiationOpenEnv"

    print(f"📦 Uploading files to {repo_id}...")

    # upload_folder with ignore_patterns to stay safe!
    upload_folder(
        folder_path=".",
        repo_id=repo_id,
        repo_type="model",
        ignore_patterns=[
            ".env",         # DO NOT UPLOAD SECRETS
            ".git/*",       # No need for git history on HF usually
            "__pycache__/*", # No python cache
            "*.pyc",
            "*.pyo",
            ".venv/*",      # No local virtual env
            "*.log"
        ]
    )

    print(f"\n✅ Successfully uploaded to: https://huggingface.co/{repo_id}")

if __name__ == "__main__":
    upload_project()
