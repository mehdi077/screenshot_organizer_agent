import base64
import os
import logging
from openai import OpenAI
from PIL import Image
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = OpenAI(
  api_key ='OPENAI_API_KEY_HERE'  # Replace with your actual API key securely
)

def encode_image_from_path(image_path):
    """
    Encodes an image file to a base64 string.

    Args:
        image_path (str): Path to the image file
    Returns:
        str: Base64 encoded string of the image
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"Error encoding image '{image_path}': {e}")
        return None

def single_interaction(message, image_path=None):
    """
    Sends a single message with optional image to the OpenAI API and returns the response.
    
    Args:
        message (str): The text message to send to the AI
        image_path (str, optional): Path to the image file
    Returns:
        str: The AI's response
    """
    # Prepare the conversation payload
    conversation = [{"type": "text", "text": message}]
    
    # Add image to conversation if provided
    if image_path:
        base64_image = encode_image_from_path(image_path)
        if base64_image:
            conversation.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Fixed model name
            messages=[{
                "role": "user",
                "content": conversation
            }]
        )
        return response.choices[0].message.content  # Fixed response parsing
    except Exception as e:
        print(f"An error occurred while communicating with OpenAI: {e}")
        return None

def is_image_file(file_name):
    """
    Checks if a file is an image based on its extension.

    Args:
        file_name (str): The name of the file
    Returns:
        bool: True if the file is an image, False otherwise
    """
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
    return os.path.splitext(file_name.lower())[1] in image_extensions

def move_files(src, dest):
    """
    Moves a file from src to dest.

    Args:
        src (str): Source file path
        dest (str): Destination file path
    """
    try:
        shutil.move(src, dest)
        logging.info(f"Moved file from '{os.path.basename(src)}' to '{os.path.basename(dest)}'")
    except Exception as e:
        logging.error(f"Error moving file '{src}' to '{dest}': {e}")

def create_directory(path):
    """
    Creates a directory if it does not exist.

    Args:
        path (str): Path of the directory to create
    """
    try:
        os.makedirs(path, exist_ok=True)
        logging.info(f"Directory '{os.path.basename(path)}' is ready")
    except Exception as e:
        logging.error(f"Error creating directory '{path}': {e}")

def get_all_image_files(directory):
    """
    Retrieves all image files in the given directory.

    Args:
        directory (str): Directory to search for image files
    Returns:
        list: List of image file paths
    """
    try:
        return [os.path.join(directory, f) for f in os.listdir(directory) 
                if os.path.isfile(os.path.join(directory, f)) and is_image_file(f)]
    except Exception as e:
        logging.error(f"Error retrieving image files from '{directory}': {e}")
        return []

def remove_empty_directories(directory):
    """
    Removes all empty subdirectories within the given directory.

    Args:
        directory (str): Directory to clean up
    """
    for root, dirs, files in os.walk(directory, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    logging.info(f"Removed empty directory '{dir_path}'")
            except Exception as e:
                logging.error(f"Error removing directory '{dir_path}': {e}")

def sanitize_filename(name):
    """
    Sanitizes a string to be used as a valid filename.

    Args:
        name (str): The original filename
    Returns:
        str: Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    
    # Replace multiple spaces with single space
    name = ' '.join(name.split())
    
    # Limit length and trim
    name = name[:100].strip()
    
    # Ensure the filename is not empty
    if not name:
        name = "unnamed"
    
    return name


def get_unique_filename(filepath):
    """
    Generates a unique filename by appending a number if the file already exists.

    Args:
        filepath (str): The original file path
    Returns:
        str: A unique file path
    """
    if not os.path.exists(filepath):
        return filepath

    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)

    counter = 1
    while True:
        new_filepath = os.path.join(directory, f"{name}_{counter}{ext}")
        if not os.path.exists(new_filepath):
            return new_filepath
        counter += 1