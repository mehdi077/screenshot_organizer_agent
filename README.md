#### ``` python3 main.py -d <folder_name> ```
https://github.com/user-attachments/assets/ac33cce9-c191-4324-8da7-9c36fed8696e
# --------------------------------------------------------------------------------
##### to rename and categorize image files inside "unstructured" folder
#### ``` python3 main.py -d <folder_name> --update ```
https://github.com/user-attachments/assets/7a495935-5f0d-4cda-ae8c-80db80daed9f
# --------------------------------------------------------------------------------
##### in case openai api call failed after the renaming stage is done use '-sk' or '--skip-renaming' flags to skip renaming
#### ``` python3 main.py -d <folder_name> --skip-renaming ```
#### ``` python3 main.py -d <folder_name> --update --skip-renaming ``` (skips renaming inside "unstructured" folder)
# --------------------------------------------------------------------------------
Here's a brief overview of the project features:

- Core Features:
  - Consolidates images from multiple folders
  - AI-powered image renaming
  - Automatic categorization into structured folders
  - Handles updates with new screenshots
  - Maintains an unstructured folder for new files

- Key Prompts Used:
  1. Image naming prompt:
    "Generate a precise, descriptive, and short title (max 5 words) for this screenshot. Focus on the main content or purpose shown."
  

  2. Categorization prompt:
    "Group the following screenshot titles into relevant one-word categories..."
  

  3. Update categorization prompt:
    "Categorize these screenshot titles into existing categories or create new ones if needed..."
  

- Technical Features:
  - Handles file deduplication
  - Sanitizes filenames
  - Supports multiple image formats
  - Command-line interface with options
  - Comprehensive logging
have fun :!~
