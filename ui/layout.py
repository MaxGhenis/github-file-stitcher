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
    GitHub Stitcher helps you combine content from various GitHub sources:
    
    - Repository files and folders
    - Pull request diffs
    - Issue discussions
    - Pattern-matched files
    
    ## Features
    - File path filtering
    - Line content filtering
    - Markdown output
    - Support for large repositories
    
    ## Help
    Need help? Check out the [documentation](https://github.com/your-repo/github-stitcher)
    """
    )
