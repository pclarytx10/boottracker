from textnode import TextNode, TextType
import os
import shutil


def copy_static_to_public(source_dir, dest_dir):
    """
    Recursively copies all contents from source directory to destination directory.
    First deletes all contents of destination directory for a clean copy.
    """
    # Clean the destination directory
    if os.path.exists(dest_dir):
        print(f"Cleaning destination directory: {dest_dir}")
        shutil.rmtree(dest_dir)
    
    # Create the destination directory
    os.mkdir(dest_dir)
    print(f"Created destination directory: {dest_dir}")
    
    # Copy all contents recursively
    _copy_directory_contents(source_dir, dest_dir)


def _copy_directory_contents(source_dir, dest_dir):
    """
    Recursively copy all files and subdirectories from source to destination.
    """
    if not os.path.exists(source_dir):
        print(f"Source directory does not exist: {source_dir}")
        return
    
    for item in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item)
        dest_path = os.path.join(dest_dir, item)
        
        if os.path.isfile(source_path):
            # Copy file
            shutil.copy(source_path, dest_path)
            print(f"Copied file: {source_path} -> {dest_path}")
        else:
            # Create directory and recursively copy its contents
            os.mkdir(dest_path)
            print(f"Created directory: {dest_path}")
            _copy_directory_contents(source_path, dest_path)


def main():
    # Copy static files to public directory
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    public_dir = os.path.join(os.path.dirname(__file__), "..", "public")
    
    copy_static_to_public(static_dir, public_dir)
    
    # Original test code
    node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(node)


if __name__ == "__main__":
    main()