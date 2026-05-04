import os
from pathlib import Path

"""Provides context about the current working directory for AI prompts."""


def get_directory_context(root: Path = None) -> str:
    """Build a context string containing the names of files and directories 
    in the current working directory."""
    if root is None:
        root = Path.cwd()

    try:
        entries = list(root.iterdir())
        files = [e.name for e in entries if e.is_file()]
        dirs = [f"{e.name}/" for e in entries if e.is_dir()]
        listing = sorted(dirs) + sorted(files)
    except PermissionError:
        listing = ["(permission denied)"]
    
    return f"Current directory: {root}\nContents:\n" + "\n".join(f"  {item}" for item in listing)


def get_directory_tree(root: Path, max_depth=3, indent=0) -> str:
    """Recursively build a directory tree string."""
    IGNORE = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.env'}
    lines = []

    try:
        entries = sorted(root.iterdir(), key=lambda e: (e.is_file(), e.name))
    except PermissionError:
        return ""

    for entry in entries:
        if entry.name in IGNORE:
            continue
        prefix = "  " * indent
        if entry.is_dir():
            lines.append(f"{prefix}📁 {entry.name}/")
            if indent < max_depth:
                lines.append(get_directory_tree(entry, max_depth, indent + 1))
        else:
            size = entry.stat().st_size
            lines.append(f"{prefix}📄 {entry.name} ({size} bytes)")

    return "\n".join(lines)


def read_file_safe(path: Path, max_bytes=10_000) -> str:
    """Read a file, truncating if too large."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_bytes:
            return text[:max_bytes] + f"\n... (truncated, {len(text)} total chars)"
        return text
    except Exception as e:
        return f"(could not read: {e})"


def build_system_context(root: Path = None) -> str:
    """Build the initial context injected at the start of every conversation."""
    if root is None:
        root = Path.cwd()
    tree = get_directory_tree(root)

    return f"""You are a coding assistant with access to the user's working directory.

        Working directory: {root}

        Directory structure:
        {tree}

        If you need the contents of a specific file to answer a question, respond with exactly:
        READ_FILE: <relative/path/to/file>

        The user's system will read it and provide the contents before you continue.
        Do not guess file contents — request them if needed."""