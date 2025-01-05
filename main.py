import os
import argparse
import tools
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_arguments():
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Screenshot Organizer Agent")
    parser.add_argument(
        '-d', '--directory',
        required=True,
        help='Path to the directory containing screenshot folders and files'
    )
    parser.add_argument(
        '-u', '--update',
        action='store_true',
        help='Update existing structured folders with new screenshots from unstructured folder'
    )
    parser.add_argument(
        '-sk', '--skip-renaming',
        action='store_true',
        help='Assume images are already named and skip renaming step'
    )
    return parser.parse_args()

def consolidate_images(original_dir):
    """
    Consolidates all image files into the original directory and handles non-image files.

    Args:
        original_dir (str): The original directory provided by the user
    """
    not_relevant_dir = os.path.join(original_dir, "not_relevant_files")
    tools.create_directory(not_relevant_dir)

    for root, dirs, files in os.walk(original_dir):
        # Skip the original directory and special directories
        if root == original_dir or root == not_relevant_dir or "structured" in root or "unstructured" in root:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            if tools.is_image_file(file):
                # Generate unique filename if file already exists
                dest_path = os.path.join(original_dir, file)
                dest_path = tools.get_unique_filename(dest_path)
                tools.move_files(file_path, dest_path)
            else:
                dest_path = os.path.join(not_relevant_dir, file)
                dest_path = tools.get_unique_filename(dest_path)
                tools.move_files(file_path, dest_path)

    tools.remove_empty_directories(original_dir)

def rename_images_with_titles(original_dir):
    """
    Renames all images in the original directory using AI-generated titles.

    Args:
        original_dir (str): The original directory containing all images
    """
    image_files = tools.get_all_image_files(original_dir)
    for image_path in image_files:
        # Skip files in special directories
        if any(x in image_path for x in ["structured", "unstructured", "not_relevant_files"]):
            continue
            
        response = tools.single_interaction(
            "Generate a precise, descriptive, and short title (max 5 words) for this screenshot. "
            "Focus on the main content or purpose shown.", 
            image_path
        )
        
        if response:
            new_title = tools.sanitize_filename(response) + os.path.splitext(image_path)[1]
            new_path = os.path.join(original_dir, new_title)
            new_path = tools.get_unique_filename(new_path)
            
            try:
                os.rename(image_path, new_path)
                logging.info(f"Renamed '{os.path.basename(image_path)}' to '{new_title}'")
            except Exception as e:
                logging.error(f"Error renaming file {image_path} to {new_title}: {e}")

def organize_into_structured(original_dir):
    """
    Organizes renamed images into structured folders based on main titles.

    Args:
        original_dir (str): The original directory containing renamed images
    """
    structured_dir = os.path.join(original_dir, "structured")
    tools.create_directory(structured_dir)

    image_files = tools.get_all_image_files(original_dir)
    # Filter out images in special directories
    image_files = [f for f in image_files if not any(x in f for x in ["structured", "unstructured", "not_relevant_files"])]

    if not image_files:
        logging.info("No images to organize.")
        return

    titles = [os.path.splitext(os.path.basename(f))[0] for f in image_files]
    titles_concatenated = "\n".join(titles)
    prompt = (
        "Group the following screenshot titles into relevant one-word categories. "
        "Create logical groups based on content similarity. "
        "Provide the result as a JSON object where keys are category names and values are lists of titles.\n\n"
        f"Titles to categorize:\n{titles_concatenated}"
        "VERY_IMPORTANT_NOTE: respond with only and only this format: -- <json_here> --"
    )

    main_titles_response = tools.single_interaction(prompt)
    main_titles_response = main_titles_response.split("--")[1].strip()
    try:
        main_titles = json.loads(main_titles_response)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing main titles: {e}")
        return

    for main_title, associated_titles in main_titles.items():
        main_folder = os.path.join(structured_dir, tools.sanitize_filename(main_title))
        tools.create_directory(main_folder)
        
        for title in associated_titles:
            for image_path in image_files:
                if os.path.splitext(os.path.basename(image_path))[0] == title:
                    destination = os.path.join(main_folder, os.path.basename(image_path))
                    destination = tools.get_unique_filename(destination)
                    tools.move_files(image_path, destination)


def update_structured_folders(original_dir, skip_renaming):
    """
    Updates structured folders with new screenshots from the unstructured folder.

    Args:
        original_dir (str): The original directory provided by the user
        skip_renaming (bool): Flag to skip renaming images in the unstructured folder
    """
    structured_dir = os.path.join(original_dir, "structured")
    unstructured_dir = os.path.join(original_dir, "unstructured")

    if not os.path.exists(unstructured_dir):
        logging.error("Unstructured directory does not exist.")
        return

    image_files = tools.get_all_image_files(unstructured_dir)
    if not image_files:
        logging.info("No new screenshots to organize.")
        return

    if not skip_renaming:
        # First, rename the images with AI-generated titles
        for image_path in image_files:
            response = tools.single_interaction(
                "Generate a precise, descriptive, and short title (max 5 words) for this screenshot. "
                "Focus on the main content or purpose shown.",
                image_path
            )

            if response:
                new_title = tools.sanitize_filename(response) + os.path.splitext(image_path)[1]
                new_path = os.path.join(unstructured_dir, new_title)
                new_path = tools.get_unique_filename(new_path)

                try:
                    os.rename(image_path, new_path)
                    logging.info(f"Renamed '{os.path.basename(image_path)}' to '{new_title}'")
                except Exception as e:
                    logging.error(f"Error renaming file {image_path} to {new_title}: {e}")
        
        # Update the list of image files after renaming
        image_files = tools.get_all_image_files(unstructured_dir)

    titles = [os.path.splitext(os.path.basename(f))[0] for f in image_files]

    # Get existing categories
    existing_categories = [d for d in os.listdir(structured_dir) 
                         if os.path.isdir(os.path.join(structured_dir, d))]

    prompt = (
        "Categorize these screenshot titles into existing categories or create new ones if needed. "
        "A strong emphasis should be placed on 'if needed', use your judgment as you see fit whether to add a certain file to an existing category, or you deem it more appropriate to create another category to contain this certain screenshot titles.\n"
        f"Existing categories are: {', '.join(existing_categories)}\n"
        "Provide the result as a JSON object where keys are category names and values are lists of titles.\n\n"
        f"Titles to categorize:\n{chr(10).join(titles)}\n"
        "VERY_IMPORTANT_NOTE: respond with only and only this format: -- <json_here> --"
    )

    main_titles_response = tools.single_interaction(prompt)

    # Extract JSON from the response
    try:
        main_titles_json = main_titles_response.split("--")[1].strip()
        main_titles = json.loads(main_titles_json)
    except (IndexError, json.JSONDecodeError) as e:
        logging.error(f"Error parsing main titles: {e}")
        return

    for main_title, associated_titles in main_titles.items():
        main_folder = os.path.join(structured_dir, tools.sanitize_filename(main_title))
        tools.create_directory(main_folder)

        for title in associated_titles:
            for image_path in image_files:
                if os.path.splitext(os.path.basename(image_path))[0] == title:
                    destination = os.path.join(main_folder, os.path.basename(image_path))
                    destination = tools.get_unique_filename(destination)
                    tools.move_files(image_path, destination)

def initialize_unstructured(original_dir):
    """
    Creates an empty 'unstructured' folder for future screenshots.

    Args:
        original_dir (str): The original directory provided by the user
    """
    unstructured_dir = os.path.join(original_dir, "unstructured")
    tools.create_directory(unstructured_dir)
    logging.info(f"Initialized 'unstructured' directory at {unstructured_dir}")

def main():
    args = parse_arguments()
    original_dir = os.path.abspath(args.directory)

    if not os.path.isdir(original_dir):
        logging.error(f"The directory '{original_dir}' does not exist.")
        return

    if args.update:
        logging.info("Updating structured folders with new screenshots...")
        update_structured_folders(original_dir, args.skip_renaming)
    else:
        logging.info("Consolidating images...")
        consolidate_images(original_dir)

        if not args.skip_renaming:
            logging.info("Renaming images with AI-generated titles...")
            rename_images_with_titles(original_dir)

        logging.info("Organizing images into structured folders...")
        organize_into_structured(original_dir)

        logging.info("Initializing 'unstructured' folder...")
        initialize_unstructured(original_dir)

    logging.info("Screenshot organization complete.")

if __name__ == "__main__":
    main()
    #updated with new