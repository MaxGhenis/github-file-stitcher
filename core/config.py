# GitHub configuration
GITHUB_MAX_FILE_SIZE = 1000000  # 1MB
BINARY_FILE_EXTENSIONS = {
    "images": ["png", "jpg", "jpeg", "gif", "bmp"],
    "documents": ["pdf", "doc", "docx", "xls", "xlsx"],
}

# UI configuration
PAGE_TITLE = "GitHub Stitcher"
PAGE_ICON = "🧵"
PAGE_LAYOUT = "wide"

# Error messages
ERROR_MESSAGES = {
    "no_input": "⚠️ Please enter at least one GitHub URL, PR link, or regex pattern.",
    "not_found": "Repository, path, PR, or issue not found. Please check the URL and ensure you have access.",
    "too_large": lambda size: f"File is too large to display (size: {size} bytes)",
    "binary_file": lambda path, type: f"[Binary {type} file: {path}]",
}
