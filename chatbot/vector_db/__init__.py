import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai.embeddings import OpenAIEmbeddings

from chatbot.models.metadata_extractor import MetadataExtractor
from chatbot.models.parent_document_retriever import ParentDocumentRetrieverMetadata
from chatbot.utils import Logger

# Set ANONYMIZED_TELEMETRY to 'False' before importing the module
os.environ["ANONYMIZED_TELEMETRY"] = "False"


class VectorDB:
    parent_dr: ParentDocumentRetrieverMetadata
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=100)  # TODO: Configurable
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=500)  # TODO: Configurable
    embedding_model: OpenAIEmbeddings
    documents_vectorstore: Chroma

    _instance = None

    def __init__(
        self,
        embedding_model_name: str,
        parent_datafile: Path,
        persist_directory: Path,
    ):

        self.embedding_model = OpenAIEmbeddings(model=embedding_model_name)
        Logger.info(
            "STARTING CHATBOT. Create vectorstore",
            extra={
                "extraFields": {
                    "parent_datafile": parent_datafile,
                    "child_datafile": persist_directory,
                }
            },
        )

        fs = LocalFileStore(parent_datafile)
        store = create_kv_docstore(fs)
        self.documents_vectorstore = Chroma(
            collection_name="full_documents",
            embedding_function=self.embedding_model,
            persist_directory=str(persist_directory),
        )

        self.parent_dr = ParentDocumentRetrieverMetadata(
            vectorstore=self.documents_vectorstore,
            docstore=store,
            child_splitter=self.child_splitter,
            parent_splitter=self.parent_splitter,
        )

    @classmethod
    def set_instance(cls, server_config):
        if cls._instance is None:
            cls._instance = VectorDB(
                embedding_model_name=server_config.openai.embedding_model,
                parent_datafile=server_config.vector_db.parent_data_file,
                persist_directory=server_config.vector_db.persist_directory,
            )
        else:
            Logger.warning("VectorDB is already initialized")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            from chatbot.config import server_config

            cls._instance = VectorDB(
                embedding_model_name=server_config.openai.embedding_model,
                parent_datafile=server_config.vector_db.parent_data_file,
                persist_directory=server_config.vector_db.persist_directory,
            )
            return cls._instance
        else:
            return cls._instance

    @staticmethod
    def load_documents(data_files: Iterable[Path], encoding: Optional[str] = None) -> List[Document]:
        loaders = [TextLoader(x, encoding=encoding, autodetect_encoding=not encoding) for x in data_files]

        documents = []
        for _l in loaders:
            documents.extend(_l.load())

        return documents

    @staticmethod
    def extract_metadata(documents: Iterable[Document]) -> List[Dict]:
        metadata_db = []

        for doc_id, document in enumerate(documents):
            # Create and store metadata
            metadata = MetadataExtractor.extract_url_metadata(document.page_content)
            metadata_db.append(metadata)

        return metadata_db

    @classmethod
    def initial_save_documents(cls, data_root: Path, data_pattern: str, encoding: Optional[str] = None):
        """Load documents to vector db"""

        vector_db = VectorDB.get_instance()

        Logger.info("Load documents to vector db")
        files = data_root.glob(f"*{data_pattern}")

        documents = vector_db.load_documents(files, encoding=encoding)

        Logger.info(f"Number of loaded data files: {len(documents)}")
        if len(documents) == 0:
            Logger.info("No documents found")
            return

        # The vectorstore to use to index the child chunks
        Logger.info("Extract metadata")
        metadata_db = vector_db.extract_metadata(documents)

        Logger.info("Add documents to vector db")
        vector_db.parent_dr.add_documents(metadatas=metadata_db, documents=documents)
        Logger.info("Done")
