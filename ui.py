import streamlit as st


def render_ui():
    github_inputs = st.text_area(
        "Enter GitHub URLs, PR links, or regex patterns (one per line):",
        height=150,
        help="Enter URLs to files, folders, PRs, or use 'regex:' prefix for file path patterns. "
        "e.g., https://github.com/username/repo/tree/branch/folder, "
        "https://github.com/username/repo/pull/123, or regex:.*\\.py$",
    )

    regex_patterns = st.text_area(
        "Enter regex patterns for text filtering (one per line):",
        height=100,
        help="These patterns will be used to filter the content of the files. Leave empty to include all content.",
    )

    filter_mode = st.radio(
        "Choose filtering mode:",
        ("Keep matching lines", "Omit matching lines"),
        help="Select whether to keep or omit the lines that match the regex patterns above.",
    )

    return github_inputs, regex_patterns, filter_mode


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
