import streamlit as st

from tools.document_loader import load_document
from services.comparison_service import ComparisonService


st.title("Document Comparator")

old_doc = st.file_uploader(
    "Old Document",
    type=["pdf", "txt", "docx"]
)

new_doc = st.file_uploader(
    "New Document",
    type=["pdf", "txt", "docx"]
)

if st.button("Analyze"):

    if old_doc and new_doc:

        old_text = load_document(old_doc)

        new_text = load_document(new_doc)

        service = ComparisonService()

        result = service.compare_documents(
            old_text,
            new_text
        )

        st.json(result)