import streamlit as st
from core.github_api import GitHubAPI
from core.config import (
    PAGE_TITLE,
    PAGE_ICON,
    PAGE_LAYOUT,
    ERROR_MESSAGES,
)
from ui.layout import render_ui, render_sidebar

# Set page config
st.set_page_config(
    page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=PAGE_LAYOUT
)


def main():
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    st.markdown(
        """
    Stitch together content from GitHub repositories, PRs, or issues. 
    Enter URLs to files, folders, PRs, issues, or use regex patterns to match file paths.
    Filter content using regex patterns to keep or omit specific lines.
    """
    )

    github_token = st.secrets["GITHUB_TOKEN"]
    github_api = GitHubAPI(github_token)

    (
        github_inputs,
        file_patterns,
        file_filter_mode,
        line_patterns,
        line_filter_mode,
    ) = render_ui()

    if st.button(
        "🧵 Stitch Content", help="Click to fetch and stitch the content"
    ):
        if not github_inputs:
            st.warning(ERROR_MESSAGES["no_input"])
            return

        inputs = [
            line.strip() for line in github_inputs.split("\n") if line.strip()
        ]
        file_patterns = [
            pattern.strip()
            for pattern in file_patterns.split("\n")
            if pattern.strip()
        ]
        line_patterns = [
            pattern.strip()
            for pattern in line_patterns.split("\n")
            if pattern.strip()
        ]

        with st.spinner("Fetching and stitching content..."):
            all_content, error_occurred = github_api.process_content(
                inputs,
                file_patterns,
                file_filter_mode == "Include matching files",
                line_patterns,
                line_filter_mode == "Include matching lines",
            )

            if error_occurred:
                st.warning(
                    "⚠️ Some errors occurred while fetching content. Please check the output below."
                )
            else:
                st.success("✅ Content stitched successfully!")

            st.subheader("Stitched Content:")
            st.code(all_content, language="text")

            st.download_button(
                "💾 Download Stitched Content",
                all_content,
                "stitched_content.md",
                help="Click to download the stitched content as a markdown file",
            )

    render_sidebar()


if __name__ == "__main__":
    main()
