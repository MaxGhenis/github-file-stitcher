import streamlit as st
from github import Github
from github_utils import process_github_content
from ui import render_ui, render_sidebar

# Set page config at the very beginning
st.set_page_config(page_title="GitHub Stitcher", page_icon="🧵", layout="wide")


def main():
    st.title("🧵 GitHub Stitcher")
    st.markdown(
        """
    Stitch together content from GitHub repositories or fetch PR diffs. 
    Enter URLs to files, folders, PRs, or use regex patterns to match file paths.
    Filter content using regex patterns to keep or omit specific lines.
    """
    )

    github_token = st.secrets["GITHUB_TOKEN"]

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
            st.warning(
                "⚠️ Please enter at least one GitHub URL, PR link, or regex pattern."
            )
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
            g = Github(github_token)
            all_content, error_occurred = process_github_content(
                g,
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
                "stitched_content.txt",
                help="Click to download the stitched content as a text file",
            )

    render_sidebar()


if __name__ == "__main__":
    main()
