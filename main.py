import os
import shutil
from src.textnode import generate_pages_recursive


def delete_public_directory(public_dir):
    """Delete everything in the public directory."""
    if os.path.exists(public_dir):
        print(f"Deleting contents of {public_dir}")
        shutil.rmtree(public_dir)
    
    # Create fresh public directory
    os.makedirs(public_dir, exist_ok=True)
    print(f"Created clean public directory: {public_dir}")


def copy_static_files(static_dir, public_dir):
    """Copy all static files from static to public directory."""
    if not os.path.exists(static_dir):
        print(f"Warning: Static directory does not exist: {static_dir}")
        return
    
    print(f"Copying static files from {static_dir} to {public_dir}")
    
    for item in os.listdir(static_dir):
        source_path = os.path.join(static_dir, item)
        dest_path = os.path.join(public_dir, item)
        
        if os.path.isdir(source_path):
            # Copy directory recursively
            shutil.copytree(source_path, dest_path)
            print(f"Copied directory: {source_path} -> {dest_path}")
        else:
            # Copy file
            shutil.copy2(source_path, dest_path)
            print(f"Copied file: {source_path} -> {dest_path}")


def main():
    # Define paths
    public_dir = "public"
    static_dir = "static"
    content_dir = "content"
    template_file = "template.html"
    
    # Step 1: Delete everything in public directory
    delete_public_directory(public_dir)
    
    # Step 2: Copy all static files from static to public
    copy_static_files(static_dir, public_dir)
    
    # Step 3: Generate pages recursively from content directory
    generate_pages_recursive(content_dir, template_file, public_dir)
    
    print("Static site generation complete!")


if __name__ == "__main__":
    main()
