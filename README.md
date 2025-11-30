# CLAMS Project Documentation Hub

This repository serves as the central publication hub for all documentation related to the CLAMS project. It aggregates generated HTML documentation from various source repositories and serves them from a single location.

## Structure

-   `index.html`: The main landing page for the entire documentation hub.
-   `docs/`: This directory contains all the generated documentation, organized by project and version.
    -   `docs/<project-name>/`: A folder for each project under the CLAMS umbrella. If the documentation for a project has multiple versions (versioned documentation), each version will have its own subdirectory.
    -   `docs/<project-name>/<version>/`: Contains the actual HTML files for a specific version of a project.
    -   `docs/<project-name>/latest/`: A stable URL that always points to the most recent version of a project's documentation.

## How It Works

The documentation source code (e.g., `.rst` files, Python docstrings) resides in the individual project repositories (e.g., `mmif-python`, `clams-python`, ...). 
Those "code" repositories are responsible for send some form of signal (e.g., via CI/CD pipelines) to trigger the documentation generation and publication process.

Currently, the process of generating and publishing documentation is manual and involves the following steps (automation via GHA workflows is planned for the future):

1. Checking out the source from a project repository.
1. Building the HTML documentation using tools like Sphinx.
1. Copying the generated HTML files into the appropriate directory within the `docs/` folder of this repository.
1. Use `build-tools/inject-header.py` to add a consistent header/navigation bar to the HTML files.
1. Committing the changes and pushing them to this repository.

This repository does not contain any documentation *source* files, only the final, published HTML artifacts.

### Building Documentation Locally

These instructions are for developers working on the documentation source files located in the `documentation/` directory. `documentation/` contains the source for the main hub pages (e.g., index, team, events) that's called "home" in the integerated publication pages. 

#### Setup

```
pip install -r build-tools/requirements.home.txt
```

#### Build

From the repository root, you build the documentation using `sphinx-build`. This generates the raw HTML files.

```bash
python build-tools/home.py 
```

This will generate the HTML files in the `docs/home` directory. There's `docs/index.html` (the main landing page) that's simply redirected to `docs/home/index.html`.

After building, you can inject the consistent CLAMS hub header into the generated files. This is necessary for the docs to look correct when deployed. The `--base-url` should point to the root of where the docs will be served. For local viewing, you can use a relative path.

```bash
# Example for deployment
python build-tools/inject-header.py docs/home --base-url https://clams.ai
```

This will edit all html files in `docs/home` in-place.

#### View Locally

```bash
# Simple HTTP server
cd docs
python -m http.server 8000
# Then open http://localhost:8000 in your browser
```

