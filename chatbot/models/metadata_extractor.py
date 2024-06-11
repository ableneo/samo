from typing import Dict

import spacy
from spacy.matcher import Matcher


class MetadataExtractor:
    """Singleton to store metadata extractor instances."""

    _model: str = "en_core_web_sm"
    _instance = None

    def __init__(self):
        # Download spacy model if not present
        if not spacy.util.is_package(self._model):
            from spacy.cli.download import download

            download(self._model)

        self.nlp = spacy.load(self._model)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MetadataExtractor()
            return cls._instance
        else:
            return cls._instance

    @classmethod
    def extract_url_metadata(cls, document_content: str) -> Dict:
        """
        Extracts metadata related to URLs from the provided document content using SpaCy.

        Args:
            document_content (str): The text content of the document.

        Returns:
            dict: A dictionary containing the extracted URL under the key "url."
                  If no matching URL is found, an empty dictionary is returned.
        """
        metadata_extractor = MetadataExtractor.get_instance()

        doc = metadata_extractor.nlp(document_content)
        matcher = Matcher(metadata_extractor.nlp.vocab)
        pattern = [{"LOWER": "web"}, {"IS_PUNCT": True}, {"LIKE_URL": True}]

        matcher.add("webURL", [pattern])
        matches = matcher(doc)

        for _, start, end in matches:
            span = doc[start:end]
            url = span.text.split("web: ", 1)[-1].split("Web: ", 1)[-1].strip()
            return {"url": url}
        return {}
