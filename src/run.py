from pathlib import Path
from src.utils import print_success

from src.nlp.text_process import (ConvertCase, RemoveDigit, RemovePunkt,
                                  RemoveSpace, TextPipeline)


class Search:
    def __init__(self, documents_path: str, stop_words: str = None) -> None:
        """
        Search Engine to search in documents.

        :param documents_path: Path to documents
        :param stop_words: Path to stop words, default is None
        """
        # crawl data
        self.data = self.crawl(documents_path)

        # Load text processor
        self.pipe = TextPipeline(ConvertCase(), RemoveDigit(), RemovePunkt(), RemoveSpace())

        # Load stop words
        self.stop_words = self.load_stop_words(stop_words)

        # index data
        self.index = self.index_data()

    def crawl(self, document_path: str) -> dict:
        """
        Crawl data from documents.

        :param document_path: Path to documents.
        :return: Data crawled.
        """
        data = {}
        for doc_path in Path(document_path).iterdir():
            if doc_path.suffix != '.txt':
                continue

            with open(doc_path) as f:
                doc_name = doc_path.stem.replace('_', ' ').title()
                data[doc_name] = f.read()

        return data

    def load_stop_words(self, stop_words: list) -> list:
        """
        Load stop words from file.

        :param stop_words: Path to stop words.
        :return: List of stop words.
        """
        if stop_words is None:
            stop_words = open('data/stop_words.txt').read()
            stop_words = stop_words.split('\n')

        # Process stop words
        stop_words = set(map(self.pipe.transform, stop_words))

        return stop_words

    def index_data(self, ) -> dict:
        """
        Index data.


        :return: Index of data.
        """
        index = {}
        for doc_name, doc_content in self.data.items():
            for word in doc_content.split():
                word = self.pipe.transform(word)
                if not word:
                    continue

                if word in self.stop_words:
                    continue

                # A more efficient way to do this is to use defaultdict
                # from collections import defaultdict
                # index = defaultdict(set)
                # index[word].add(doc_name)
                if word in index:
                    index[word].add(doc_name)
                else:
                    index[word] = {doc_name}

        return index

    def search(self, query: str) -> list:
        """
        Search query in documents.

        :param query: Query to search.
        :return: List of documents.
        """
        query = self.pipe.transform(query)
        search_tokens = query.split()
        docs = []
        for token in search_tokens:
            docs.extend(self.index.get(token, []))

        return docs


if __name__ == '__main__':
    searcher = Search('data/documents')

    # Search query
    while True:
        query = input('Search to find a doc (q to quit): ')
        if query.lower() == 'q':
            break

        docs = searcher.search(query)
        for doc_name in docs:
            print_success(f'- {doc_name}')
