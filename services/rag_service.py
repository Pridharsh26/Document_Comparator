import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
FAISS_INDEX_PATH = "data/hr_policy_faiss_index"
HR_POLICY_PDF_PATH = "data/hr_policy_manual.pdf"


class RagService:
    def __init__(self) -> None:
        self.vectorstore = None
        self._available = None

    def _check_availability(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            import faiss
            from langchain_community.vectorstores import FAISS
            self._available = True
            return True
        except Exception as exc:
            logger.warning("RAG dependencies unavailable, skipping FAISS index: %s", exc)
            self._available = False
            return False

    def _ensure_knowledge_base(self) -> None:
        if not self._check_availability():
            return
        self._ensure_data_dir()
        if not os.path.exists(HR_POLICY_PDF_PATH):
            try:
                from services.hr_policy_generator import HrPolicyPDFGenerator
                HrPolicyPDFGenerator().generate(HR_POLICY_PDF_PATH)
            except Exception as exc:
                logger.warning("Failed to generate HR policy PDF: %s", exc)

        if os.path.exists(FAISS_INDEX_PATH):
            try:
                self._load_index()
                return
            except Exception as exc:
                logger.warning("Failed to load existing FAISS index: %s", exc)
        if os.path.exists(HR_POLICY_PDF_PATH):
            self._build_index()

    def _load_index(self) -> None:
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import FAISS

            embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            self.vectorstore = FAISS.load_local(
                FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
            )
        except Exception as exc:
            logger.warning("Failed to load FAISS index: %s", exc)
            raise

    def _build_index(self) -> None:
        try:
            from services.document_reader import read_document
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import FAISS

            text = read_document(HR_POLICY_PDF_PATH)
            chunks = self._chunk_text(text, chunk_size_chars=1500, overlap_chars=200)
            docs = [{"page_content": chunk} for chunk in chunks]
            embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            self.vectorstore = FAISS.from_documents(docs, embeddings)
            self.vectorstore.save_local(FAISS_INDEX_PATH)
            logger.info("Built FAISS RAG index with %d chunks", len(docs))
        except Exception as exc:
            logger.warning("Failed to build FAISS index: %s", exc)
            self.vectorstore = None

    @staticmethod
    def _chunk_text(text: str, chunk_size_chars: int = 1500, overlap_chars: int = 200) -> list:
        text = text.replace("\r\n", "\n")
        cleaned = []
        current = ""
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if len(current) + len(line) + 1 > chunk_size_chars:
                if current:
                    cleaned.append(current)
                current = line
            else:
                current = f"{current}\n{line}" if current else line
        if current:
            cleaned.append(current)

        overlapped = []
        for idx, chunk in enumerate(cleaned):
            if idx > 0 and overlap_chars > 0:
                prev = cleaned[idx - 1]
                overlap = prev[-overlap_chars:] if len(prev) > overlap_chars else prev
                overlapped.append(f"{overlap}\n{chunk}")
            else:
                overlapped.append(chunk)
        return overlapped

    def retrieve(self, query: str, top_k: int = 3) -> str:
        if self.vectorstore is None:
            self._ensure_knowledge_base()
        if self.vectorstore is None:
            return ""
        docs = self.vectorstore.similarity_search(query, k=top_k)
        return "\n\n".join(doc.page_content for doc in docs)
