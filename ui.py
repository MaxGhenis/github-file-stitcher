import streamlit as st


def render_ui():
    github_inputs = st.text_area(
        "Enter GitHub URLs, PR links, or regex patterns (one per line):",
        height=150,
        help="Enter URLs to files, folders, PRs, or use 'regex:' prefix for file path patterns. "
        "e.g., https://github.com/username/repo/tree/branch/folder, "
        "https://github.com/username/repo/pull/123, or regex:.*\\.py$",
    )
    # Regex filtering to include or exclude files.
    file_patterns = st.text_area(
        "Enter regex patterns for file filtering (one per line):",
        height=100,
        help="These patterns will be used to filter which files to include or exclude. Leave empty to include all files. "
        "e.g., .*\\.py$ for Python files, or .*test.* for test files",
    )
    file_filter_mode = st.radio(
        "Choose filtering mode:",
        ("Include matching files", "Exclude matching files"),
        help="Select whether to include or exclude the files that match the regex patterns above.",
    )
    # Regex filtering to include or exclude lines.
    line_patterns = st.text_area(
        "Enter regex patterns for text filtering (one per line):",
        height=100,
        help="These patterns will be used to filter the content of the files. Leave empty to include all content.",
    )
    line_filter_mode = st.radio(
        "Choose filtering mode:",
        ("Include matching lines", "Exclude matching lines"),
        help="Select whether to include or exclude the lines that match the regex patterns above.",
    )

    return (
        github_inputs,
        file_patterns,
        file_filter_mode,
        line_patterns,
        line_filter_mode,
    )


def render_sidebar():
    st.sidebar.title("About")
    st.sidebar.info(
        """
        GitHub Stitcher was created by [Max Ghenis](mailto:mghenis@gmail.com).

        This tool allows you to:
        - Fetch content from GitHub files, folders, or entire repositories
        - Fetch diffs from Pull Requests
        - Use regex patterns to filter specific file paths
        - Keep or omit lines based on regex patterns
        - Combine the filtered content into a single, easy-to-use output
        """
    )
