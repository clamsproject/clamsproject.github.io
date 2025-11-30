#!/usr/bin/env python3
"""
Header injection script for CLAMS Documentation Hub.

This script scans a project's documentation directory, discovers all version
subdirectories, and injects a consistent navigation header into every HTML file.
The header includes the CLAMS logo, navigation links to all projects, and a
version selector for the current project.

Usage:
    python build/inject.py docs/mmif-python/
    python build/inject.py docs/home/
"""

import argparse
import re
import sys
from pathlib import Path


# Header template with embedded CSS
# Supports both light and dark modes (Furo theme compatibility)
HEADER_TEMPLATE = '''<!-- CLAMS Hub Version Header - Injected -->
<style>
.clams-version-header {{
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    padding: 8px 16px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
}}
@media (prefers-color-scheme: dark) {{
    body:not([data-theme="light"]) .clams-version-header {{
        background: #1a1a1a;
        border-bottom-color: #333;
    }}
    body:not([data-theme="light"]) .clams-version-header a {{
        color: #6cb6ff;
    }}
    body:not([data-theme="light"]) .clams-version-header select {{
        background: #2d2d2d;
        color: #e0e0e0;
        border-color: #444;
    }}
    body:not([data-theme="light"]) .clams-version-header .nav-link.active {{
        background: #333;
    }}
}}
body[data-theme="dark"] .clams-version-header {{
    background: #1a1a1a;
    border-bottom-color: #333;
}}
body[data-theme="dark"] .clams-version-header a {{
    color: #6cb6ff;
}}
body[data-theme="dark"] .clams-version-header select {{
    background: #2d2d2d;
    color: #e0e0e0;
    border-color: #444;
}}
body[data-theme="dark"] .clams-version-header .nav-link.active {{
    background: #333;
}}
.clams-version-header a {{
    color: #008AFF;
    text-decoration: none;
}}
.clams-version-header a:hover {{
    text-decoration: underline;
}}
.clams-version-header .header-left {{
    display: flex;
    align-items: center;
    gap: 16px;
}}
.clams-version-header .logo {{
    height: 28px;
    width: auto;
}}
.clams-version-header .project-nav {{
    display: flex;
    align-items: center;
    gap: 4px;
}}
.clams-version-header .nav-link {{
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 13px;
}}
.clams-version-header .nav-link:hover {{
    background: #e9ecef;
    text-decoration: none;
}}
.clams-version-header .nav-link.active {{
    background: #e9ecef;
    font-weight: 600;
}}
.clams-version-header .header-right {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.clams-version-header select {{
    padding: 4px 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 13px;
}}
</style>
<div class="clams-version-header">
    <div class="header-left">
        <a href="{hub_url}" title="CLAMS Documentation Hub">
            <img src="{logo_url}" alt="CLAMS" class="logo">
        </a>
        <nav class="project-nav">
{project_nav_links}
        </nav>
    </div>
    <div class="header-right">
        <select onchange="if(this.value) window.location.href=this.value;">
            <option value="">Switch version...</option>
{version_options}
        </select>
    </div>
</div>
<!-- End CLAMS Hub Version Header -->
'''

# Header template for non-versioned projects (no version dropdown)
HEADER_TEMPLATE_NO_VERSION = '''<!-- CLAMS Hub Version Header - Injected -->
<style>
.clams-version-header {{
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    padding: 8px 16px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}}
@media (prefers-color-scheme: dark) {{
    body:not([data-theme="light"]) .clams-version-header {{
        background: #1a1a1a;
        border-bottom-color: #333;
    }}
    body:not([data-theme="light"]) .clams-version-header a {{
        color: #6cb6ff;
    }}
    body:not([data-theme="light"]) .clams-version-header .nav-link.active {{
        background: #333;
    }}
}}
body[data-theme="dark"] .clams-version-header {{
    background: #1a1a1a;
    border-bottom-color: #333;
}}
body[data-theme="dark"] .clams-version-header a {{
    color: #6cb6ff;
}}
body[data-theme="dark"] .clams-version-header .nav-link.active {{
    background: #333;
}}
.clams-version-header a {{
    color: #008AFF;
    text-decoration: none;
}}
.clams-version-header a:hover {{
    text-decoration: underline;
}}
.clams-version-header .header-left {{
    display: flex;
    align-items: center;
    gap: 16px;
}}
.clams-version-header .logo {{
    height: 28px;
    width: auto;
}}
.clams-version-header .project-nav {{
    display: flex;
    align-items: center;
    gap: 4px;
}}
.clams-version-header .nav-link {{
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 13px;
}}
.clams-version-header .nav-link:hover {{
    background: #e9ecef;
    text-decoration: none;
}}
.clams-version-header .nav-link.active {{
    background: #e9ecef;
    font-weight: 600;
}}
</style>
<div class="clams-version-header">
    <div class="header-left">
        <a href="{hub_url}" title="CLAMS Documentation Hub">
            <img src="{logo_url}" alt="CLAMS" class="logo">
        </a>
        <nav class="project-nav">
{project_nav_links}
        </nav>
    </div>
</div>
<!-- End CLAMS Hub Version Header -->
'''


def parse_version(version_str):
    """Parse version string for sorting. Returns tuple for comparison."""
    # Handle 'latest' specially - it should come first
    if version_str == 'latest':
        return (float('inf'),)

    # Try to parse as semantic version
    parts = []
    for part in version_str.lstrip('v').split('.'):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(part)
    return tuple(parts)


def discover_versions(project_dir):
    """
    Discover all version subdirectories in the project directory.

    Args:
        project_dir: Path to the project documentation directory

    Returns:
        List of version strings, sorted with latest/newest first
    """
    versions = []
    project_path = Path(project_dir)

    if not project_path.is_dir():
        raise ValueError(f"Directory not found: {project_dir}")

    for item in project_path.iterdir():
        if item.is_dir():
            # Check if it looks like a version directory
            name = item.name
            # Accept: 1.0.0, v1.0.0, latest, etc.
            if name == 'latest' or re.match(r'^v?\d+', name):
                versions.append(name)

    # Sort versions: latest first, then by version number (newest first)
    versions.sort(key=parse_version, reverse=True)

    return versions


def discover_projects(docs_root):
    """
    Discover all project subdirectories in the docs root.

    Args:
        docs_root: Path to the docs/ directory

    Returns:
        Dict mapping project names to their info (is_versioned)
    """
    projects = {}
    docs_path = Path(docs_root)

    if not docs_path.is_dir():
        return projects

    for item in docs_path.iterdir():
        if item.is_dir():
            name = item.name
            # Skip assets and other non-project directories
            if name in ('assets', '.git', '__pycache__'):
                continue
            # Check if it has version subdirectories
            has_versions = any(
                subdir.is_dir() and (
                    subdir.name == 'latest' or
                    re.match(r'^v?\d+', subdir.name)
                )
                for subdir in item.iterdir()
            )
            # Check if it has HTML files directly (non-versioned)
            has_html = any(
                f.suffix == '.html' for f in item.iterdir() if f.is_file()
            )
            if has_versions or has_html:
                projects[name] = {'is_versioned': has_versions}

    return projects


def generate_project_nav_links(projects, current_project, base_url):
    """
    Generate HTML for project navigation links.

    Args:
        projects: Dict mapping project names to their info
        current_project: Name of the current project
        base_url: Base URL for the documentation hub

    Returns:
        String of HTML anchor elements
    """
    links = []

    for project in 'home mmif mmif-python clams-python aapb-annotations aapn-evaluations'.split():
        if project not in projects:
            continue
        info = projects[project]
        # Use absolute URLs based on base_url
        if info['is_versioned']:
            url = f"{base_url}/{project}/latest/"
        else:
            url = f"{base_url}/{project}/"

        active_class = ' active' if project == current_project else ''
        links.append(
            f'            <a href="{url}" '
            f'class="nav-link{active_class}">{project}</a>'
        )

    return '\n'.join(links)


def generate_version_options(versions, current_version, base_url, project_name):
    """
    Generate HTML option elements for the version selector.

    Args:
        versions: List of all versions
        current_version: The version currently being viewed
        base_url: Base URL for the documentation hub
        project_name: Name of the current project

    Returns:
        String of HTML option elements
    """
    options = []
    for version in versions:
        # Use absolute URL for version switching
        url = f"{base_url}/{project_name}/{version}/"

        if version == current_version:
            options.append(
                f'            <option value="" disabled selected>'
                f'{version} (current)</option>'
            )
        else:
            label = version
            if version == 'latest':
                label = 'latest (development)'
            options.append(
                f'            <option value="{url}">{label}</option>'
            )

    return '\n'.join(options)


def generate_header(project_name, current_version, versions, projects,
                    base_url, is_versioned=True):
    """
    Generate the complete header HTML for injection.

    Args:
        project_name: Name of the project
        current_version: Current version being processed (None for non-versioned)
        versions: List of all available versions (empty for non-versioned)
        projects: Dict of all projects in the hub
        base_url: Base URL for the documentation hub
        is_versioned: Whether this project has versioned subdirectories

    Returns:
        Complete header HTML string
    """
    # Build absolute URLs from base_url
    hub_url = f"{base_url}/"
    logo_url = f"{base_url}/home/_static/clams-logo.png"

    project_nav_links = generate_project_nav_links(
        projects, project_name, base_url
    )

    if is_versioned and versions:
        version_options = generate_version_options(
            versions, current_version, base_url, project_name
        )
        return HEADER_TEMPLATE.format(
            project_name=project_name,
            current_version=current_version,
            version_options=version_options,
            project_nav_links=project_nav_links,
            hub_url=hub_url,
            logo_url=logo_url
        )
    else:
        return HEADER_TEMPLATE_NO_VERSION.format(
            project_nav_links=project_nav_links,
            hub_url=hub_url,
            logo_url=logo_url
        )


def inject_header_into_file(file_path, header_html):
    """
    Inject the header into a single HTML file.

    The header is inserted right after the <body> tag.
    If the file already has an injected header, it is replaced.

    Args:
        file_path: Path to the HTML file
        header_html: The header HTML to inject

    Returns:
        True if injection was successful, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {file_path}: {e}", file=sys.stderr)
        return False

    # Remove existing injected header if present
    content = re.sub(
        r'<!-- CLAMS Hub Version Header - Injected -->.*?'
        r'<!-- End CLAMS Hub Version Header -->\n?',
        '',
        content,
        flags=re.DOTALL
    )

    # Find the <body> tag and inject after it
    # Handle various body tag formats: <body>, <body class="...">, etc.
    body_pattern = r'(<body[^>]*>)'
    match = re.search(body_pattern, content)

    if not match:
        print(f"  Warning: No <body> tag found in {file_path}", file=sys.stderr)
        return False

    # Insert header after body tag
    insert_pos = match.end()
    new_content = content[:insert_pos] + '\n' + header_html + content[insert_pos:]

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"  Error writing {file_path}: {e}", file=sys.stderr)
        return False


def process_version_directory(version_dir, header_html):
    """
    Process all HTML files in a version directory.

    Args:
        version_dir: Path to the version directory
        header_html: The header HTML to inject

    Returns:
        Tuple of (success_count, total_count)
    """
    version_path = Path(version_dir)
    html_files = list(version_path.rglob('*.html'))

    success_count = 0
    for html_file in html_files:
        if inject_header_into_file(html_file, header_html):
            success_count += 1

    return success_count, len(html_files)


def main():
    parser = argparse.ArgumentParser(
        description='Inject version navigation header into documentation HTML files'
    )
    parser.add_argument(
        'project_dir',
        help='Path to project documentation directory (e.g., docs/mmif-python/)'
    )
    parser.add_argument(
        '--base-url',
        default='https://clams.ai',
        help='Base URL for documentation hub (default: https://clams.ai/docs)'
    )
    parser.add_argument(
        '--project-name',
        help='Project name to display (default: derived from directory name)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    project_dir = Path(args.project_dir)

    # Derive project name from directory if not specified
    project_name = args.project_name or project_dir.name

    # Determine docs root (parent of project directory)
    docs_root = project_dir.parent

    # Discover all projects in the hub
    projects = discover_projects(docs_root)
    if projects:
        print(f"Found projects: {', '.join(sorted(projects.keys()))}")
    else:
        print("Warning: No projects found in docs/", file=sys.stderr)
        projects = {project_name: {'is_versioned': False}}

    # Discover versions for this project
    print(f"Scanning {project_dir} for versions...")
    try:
        versions = discover_versions(project_dir)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    is_versioned = len(versions) > 0

    if args.dry_run:
        print("\nDry run mode - no changes will be made\n")

    total_success = 0
    total_files = 0

    if is_versioned:
        # Versioned project: process each version directory
        print(f"Found {len(versions)} versions: {', '.join(versions)}")

        for version in versions:
            # Skip 'latest' if it's just a redirect (only has index.html)
            version_dir = project_dir / version
            if version == 'latest':
                files = list(version_dir.iterdir())
                if len(files) == 1 and files[0].name == 'index.html':
                    print(f"Skipping {version}/ (redirect only)")
                    continue

            # Generate header for this specific version
            header_html = generate_header(
                project_name,
                version,
                versions,
                projects,
                args.base_url,
                is_versioned=True
            )

            if args.dry_run:
                html_count = len(list(version_dir.rglob('*.html')))
                print(f"  {version}: would inject into {html_count} files")
                total_files += html_count
            else:
                print(f"Processing {version}...")
                success, total = process_version_directory(version_dir, header_html)
                print(f"  Injected header into {success}/{total} files")
                total_success += success
                total_files += total

        # Generate latest redirect if 'latest' doesn't exist as a real version
        if 'latest' not in versions and versions:
            highest_version = versions[0]
            latest_dir = project_dir / 'latest'

            if args.dry_run:
                print(f"  Would create latest/ redirect to {highest_version}")
            else:
                latest_dir.mkdir(exist_ok=True)
                redirect_html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Redirecting to latest version...</title>
    <meta http-equiv="refresh" content="0;url=../{highest_version}/" />
    <link rel="canonical" href="../{highest_version}/" />
</head>
<body>
    <p>Redirecting to <a href="../{highest_version}/">version {highest_version}</a>.</p>
</body>
</html>
'''
                (latest_dir / 'index.html').write_text(redirect_html)
                print(f"  Created latest/ redirect to {highest_version}")
    else:
        # Non-versioned project: process the directory itself
        print("No version directories found - treating as non-versioned project")

        # Generate header without version selector
        header_html = generate_header(
            project_name,
            None,
            [],
            projects,
            args.base_url,
            is_versioned=False
        )

        if args.dry_run:
            html_count = len(list(project_dir.rglob('*.html')))
            print(f"  Would inject into {html_count} files")
            total_files += html_count
        else:
            print(f"Processing {project_name}...")
            success, total = process_version_directory(project_dir, header_html)
            print(f"  Injected header into {success}/{total} files")
            total_success += success
            total_files += total

    # Summary
    print(f"\nComplete: {total_success}/{total_files} files processed")


if __name__ == '__main__':
    main()
