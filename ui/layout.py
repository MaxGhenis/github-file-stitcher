import streamlit as st
from .components import (
    github_input_area,
    file_pattern_input,
    line_pattern_input,
    filter_mode_selector,
)


def render_ui():
    """Render the main UI components and return their values."""
    github_inputs = github_input_area()

    with st.expander("Advanced Filtering Options"):
        col1, col2 = st.columns(2)

        with col1:
            file_patterns = file_pattern_input()
            file_filter_mode = filter_mode_selector(
                "File Filter Mode",
                "Choose whether to include or exclude files matching the patterns",
            )

        with col2:
            line_patterns = line_pattern_input()
            line_filter_mode = filter_mode_selector(
                "Line Filter Mode",
                "Choose whether to include or exclude lines matching the patterns",
            )

    return (
        github_inputs,
        file_patterns,
        file_filter_mode,
        line_patterns,
        line_filter_mode,
    )


def render_sidebar():
    """Render the sidebar with information and help."""
    st.sidebar.markdown(
        """
        # About
        GitHub Stitcher helps you combine and filter content from GitHub. Enter URLs or patterns in any format:

        ### 📄 Files
        ```
        github.com/owner/repo/blob/branch/file.py
        ```

        ### 📁 Directories
        ```
        github.com/owner/repo/tree/branch/dir
        ```

        ### 🔍 Pattern Matching
        ```
        regex:.*\.py$
        ```

        ### 🔀 Pull Requests
        ```
        github.com/owner/repo/pull/123
        ```

        ### ❓ Issues
        ```
        github.com/owner/repo/issues/456
        ```

        ### 💡 Tips
        - Enter multiple URLs (one per line)
        - Use regex patterns to filter specific files
        - Branch names can include slashes
        - Default branch is used if not specified
        - Expand "Advanced Filtering" for more options

        ### 🛠️ Advanced Features
        - Line filtering with regex
        - Include/exclude mode for both files and lines
        - Syntax highlighting
        - Downloadable output

        ### 🔗 Links
        - [Documentation](https://github.com/your-username/github-stitcher)
        - [Report an Issue](https://github.com/your-username/github-stitcher/issues)
        
        Created by [Max Ghenis](https://github.com/maxghenis)
        """
    )
