import streamlit as st


def github_input_area():
    return st.text_area(
        "GitHub URLs",
        height=150,
        help=(
            "Enter GitHub URLs (one per line) for:\n"
            "- Repository files/folders\n"
            "- Pull requests\n"
            "- Issues\n"
            "- Or use regex: prefix for regex patterns"
        ),
        placeholder=(
            "Examples:\n"
            "github.com/owner/repo/blob/main/file.py\n"
            "github.com/owner/repo/pull/123\n"
            "github.com/owner/repo/issues/456\n"
            "regex:.*\\.py$"
        ),
    )


def file_pattern_input():
    return st.text_area(
        "File Path Patterns",
        height=100,
        help="Enter regex patterns to filter files by path (one per line)",
        placeholder="Example:\n.*\\.py$\n.*\\.md$",
    )


def line_pattern_input():
    return st.text_area(
        "Line Content Patterns",
        height=100,
        help="Enter regex patterns to filter lines by content (one per line)",
        placeholder="Example:\nTODO:\nFIXME:",
    )


def filter_mode_selector(label, help_text):
    return st.radio(
        label,
        ["Include matching files", "Exclude matching files"],
        help=help_text,
    )
