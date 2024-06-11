import uuid
from typing import Dict, List, Optional

from langchain.retrievers import ParentDocumentRetriever
from langchain.schema.document import Document


class ParentDocumentRetrieverMetadata(ParentDocumentRetriever):
    """Extend ParentDocumentRetriever to handle metadata during document addition."""

    def add_documents(
        self,
        documents: List[Document],
        metadatas: Optional[List[Dict[str, any]]] = None,
        ids: Optional[List[str]] = None,
        add_to_docstore: bool = True,
    ) -> None:
        if metadatas:
            for x, doc in enumerate(documents):
                if metadatas[x]:
                    for key, value in metadatas[x].items():
                        doc.metadata[key] = value

        """Adds documents and metadata to the docstore and vectorstores.

        Args:
            documents: List of documents to add
            metadatas: Optional list of metadata dictionaries for each document.
                If provided, should be the same length as the list of documents.
            ids: Optional list of ids for documents. If provided should be the same
                length as the list of documents. Can be provided if parent documents
                are already in the document store and you don't want to re-add
                to the docstore. If not provided, random UUIDs will be used as
                ids.
            add_to_docstore: Boolean of whether to add documents to docstore.
                This can be false if and only if `ids` are provided. You may want
                to set this to False if the documents are already in the docstore
                and you don't want to re-add them.
        """
        if self.parent_splitter is not None:
            documents = self.parent_splitter.split_documents(documents)
        if ids is None:
            doc_ids = [str(uuid.uuid4()) for _ in documents]
            if not add_to_docstore:
                raise ValueError("If ids are not passed in, `add_to_docstore` MUST be True")
        else:
            if len(documents) != len(ids):
                raise ValueError(
                    "Got uneven list of documents and ids. " "If `ids` is provided, should be same length as `documents`."
                )
            doc_ids = ids

        docs = []
        full_docs = []
        for i, doc in enumerate(documents):
            _id = doc_ids[i]
            sub_docs = self.child_splitter.split_documents([doc])

            for _doc in sub_docs:
                _doc.metadata[self.id_key] = _id
            docs.extend(sub_docs)
            full_docs.append((_id, doc))
        self.vectorstore.add_documents(docs)
        if add_to_docstore:
            self.docstore.mset(full_docs)
