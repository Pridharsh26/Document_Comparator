import streamlit as st
import json

from tools.document_loader import load_document
from tools.chunking import create_chunks
from tools.semantic_search import compare_chunks

from agents.document_analyzer import DocumentAnalyzerAgent
from agents.impact_agent import ImpactAgent

from utils.parser import save_json


st.set_page_config(
    page_title="Document Comparator",
    layout="wide"
)

st.title("📄 AI Document Comparator")

old_file = st.file_uploader(
    "Upload Old Document",
    type=["pdf", "docx", "txt"]
)

new_file = st.file_uploader(
    "Upload New Document",
    type=["pdf", "docx", "txt"]
)

if st.button("Analyze"):

    if not old_file or not new_file:
        st.warning("Please upload both documents.")
        st.stop()

    try:

        # ----------------------------
        # Load Documents
        # ----------------------------
        with st.spinner("Loading documents..."):
            old_text = load_document(old_file)
            new_text = load_document(new_file)

        # ----------------------------
        # Create Chunks
        # ----------------------------
        with st.spinner("Creating chunks..."):
            old_chunks = create_chunks(old_text)
            new_chunks = create_chunks(new_text)

        # ----------------------------
        # Semantic Comparison
        # ----------------------------
        with st.spinner("Performing semantic comparison..."):
            changes = compare_chunks(
                old_chunks,
                new_chunks
            )

        # ----------------------------
        # Document Analysis
        # ----------------------------
        with st.spinner("Running Document Analyzer..."):
            doc_agent = DocumentAnalyzerAgent()
            doc_result = doc_agent.analyze(changes)

        # ----------------------------
        # Parse Document Analysis
        # ----------------------------
        if isinstance(doc_result, str):

            cleaned = doc_result.strip()

            if cleaned.startswith("```json"):
                cleaned = cleaned.replace(
                    "```json",
                    ""
                )

                cleaned = cleaned.replace(
                    "```",
                    ""
                ).strip()

            try:
                doc_result = json.loads(cleaned)
            except Exception:
                pass

        if isinstance(doc_result, dict):
            doc_result = [doc_result]

        # ----------------------------
        # Impact Analysis
        # ----------------------------
        with st.spinner("Running Impact Analyzer..."):
            impact_agent = ImpactAgent()
            impact_result = impact_agent.analyze(doc_result)

        st.success("✅ Analysis Completed")

        # ==================================================
        # DOCUMENT ANALYSIS UI
        # ==================================================

        st.markdown("---")
        st.markdown("## 📄 Document Analysis")

        if isinstance(doc_result, list) and len(doc_result) > 0:

            tab_names = []

            for i, item in enumerate(doc_result):

                tab_names.append(
                    item.get(
                        "rule_name",
                        f"Rule {i+1}"
                    )
                )

            tabs = st.tabs(tab_names)

            for tab, item in zip(tabs, doc_result):

                with tab:

                    change_type = item.get(
                        "change_type",
                        "UNKNOWN"
                    )

                    if change_type == "ADDED":
                        st.success(
                            f"Change Type: {change_type}"
                        )

                    elif change_type == "MODIFIED":
                        st.warning(
                            f"Change Type: {change_type}"
                        )

                    elif change_type == "REMOVED":
                        st.error(
                            f"Change Type: {change_type}"
                        )

                    else:
                        st.info(
                            f"Change Type: {change_type}"
                        )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.subheader("Old Version")

                        st.text_area(
                            "Old Text",
                            item.get(
                                "old_text",
                                "N/A"
                            ),
                            height=220,
                            disabled=True,
                            key=f"old_{item.get('rule_name', '')}"
                        )

                    with col2:

                        st.subheader("New Version")

                        st.text_area(
                            "New Text",
                            item.get(
                                "new_text",
                                "N/A"
                            ),
                            height=220,
                            disabled=True,
                            key=f"new_{item.get('rule_name', '')}"
                        )

                    st.subheader("Summary")

                    st.info(
                        item.get(
                            "summary",
                            "No summary available."
                        )
                    )

        else:
            st.write(doc_result)

        # ==================================================
        # IMPACT ANALYSIS UI
        # ==================================================

        st.markdown("---")
        st.markdown("## 🎯 Impact Analysis")
        
        try:
            impact_data = json.loads(impact_result)
        
            col1, col2 = st.columns(2)
        
            with col1:
                st.subheader("🔄 What Changed")
                st.info(impact_data.get("what_changed", "N/A"))
        
            with col2:
                risk = impact_data.get("risk_level", "N/A")
        
                if risk.upper() == "HIGH":
                    st.error(f"Risk Level: {risk}")
                elif risk.upper() == "MEDIUM":
                    st.warning(f"Risk Level: {risk}")
                else:
                    st.success(f"Risk Level: {risk}")
        
            st.subheader("🏢 Business Impact")
            st.write(impact_data.get("business_impact", "N/A"))
        
            st.subheader("⚖️ Compliance Impact")
            st.write(impact_data.get("compliance_impact", "N/A"))
        
            st.subheader("👥 Stakeholders Affected")
            st.write(impact_data.get("stakeholders_affected", "N/A"))
        
            st.subheader("✅ Recommended Actions")
            st.write(impact_data.get("recommended_actions", "N/A"))
        
            st.subheader("📌 Executive Summary")
            st.success(impact_data.get("executive_summary", "N/A"))
        
        except Exception:
            st.code(impact_result, language="json")

        # ==================================================
        # DOWNLOADS
        # ==================================================

        st.markdown("---")
        st.markdown("## 📥 Download Results")

        st.download_button(
            label="Download Document Analysis",
            data=json.dumps(
                doc_result,
                indent=2
            ),
            file_name="document_analysis.json",
            mime="application/json"
        )

        st.download_button(
            label="Download Impact Analysis",
            data=str(
                impact_result
            ),
            file_name="impact_analysis.txt",
            mime="text/plain"
        )

    except Exception as e:

        st.error(
            f"Application Error: {str(e)}"
        )