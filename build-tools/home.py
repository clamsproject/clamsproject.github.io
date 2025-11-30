import subprocess
import os
import shutil

def build_home_docs():
    """
    Builds the hub home page documentation from the 'documentation' directory.
    """
    source_dir = "documentation"
    output_dir = "docs/home"

    print(f"--- Building home documentation ---")
    print(f"Source: {source_dir}")
    print(f"Output: {output_dir}")

    # Ensure the output directory exists and is clean
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    try:
        # Run the sphinx-build command
        subprocess.run(
            ["sphinx-build", "-b", "html", source_dir, output_dir],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Successfully built documentation in {output_dir}")
    except subprocess.CalledProcessError as e:
        print("!!! Sphinx build failed !!!")
        print(f"Return code: {e.returncode}")
        print("--- STDOUT ---")
        print(e.stdout)
        print("--- STDERR ---")
        print(e.stderr)
        exit(1)

if __name__ == "__main__":
    build_home_docs()
