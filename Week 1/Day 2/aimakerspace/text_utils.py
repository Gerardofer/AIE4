import os
import fitz  # PyMuPDF
import re
from typing import List



class TextFileLoader:
    def __init__(self, path: str, encoding: str = "utf-8"):
        self.documents = []
        self.path = path
        self.encoding = encoding

    def load(self):
        if os.path.isdir(self.path):
            self.load_directory()
        elif os.path.isfile(self.path):
            if self.path.endswith(".txt"):
                self.load_text_file()
            elif self.path.endswith(".pdf"):
                self.load_pdf_file()
            else: 
                raise ValueError(
                    "Provided file is not a .txt or .pdf file."
                )
        else:
            raise ValueError(
                "Provided path is neither a valid directory nor a .txt or .pdf file."
            )

    def load_text_file(self):
        with open(self.path, "r", encoding=self.encoding) as f:
            self.documents.append(f.read())

    def load_pdf_file(self):
        doc = fitz.open(self.path)
        text = ''
        for page in doc:
            text += page.get_text()
        self.documents.append(text)
        doc.close()

    def load_directory(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".txt"):
                    with open(
                        os.path.join(root, file), "r", encoding=self.encoding
                    ) as f:
                        self.documents.append(f.read())
                elif file.endswith(".pdf"):
                    doc = fitz.open(os.path.join(root, file))
                    text = ''
                    for page in doc:
                        text += page.get_text()
                    self.documents.append(text)
                    doc.close()

    def load_documents(self):
        self.load()
        return self.documents

class CharacterTextSplitter:
    def __init__(self, max_chunks: int = 2, max_chunk_size = 1000, overlap_size = 100):
        self.max_chunks = max_chunks
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size

    def split(self, text: str) -> List[str]:
        pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        paragraphs = re.split(pattern, text)
        chunks = []
        current_chunk = []
        current_length = 0

        for paragraph in paragraphs:

            if not paragraph.split():
                continue

            proposed_length = current_length + len(paragraph) + 1

            if current_chunk and proposed_length > self.max_chunk_size:
                joined_text = '\n'.join(current_chunk)
                if len(joined_text) > self.overlap_size:
                    chunks.append(joined_text[:-self.overlap_size])
                    overlap_text = joined_text[-self.overlap_size:]
                    current_chunk = [overlap_text + paragraph]
                    current_length = len(overlap_text) + len(paragraph) + 1
                else:
                    current_chunk.append(paragraph)
                    current_length += len(paragraph) + 1
            else:
                current_chunk.append(paragraph)
                current_length += len(paragraph) + 1

            if len(current_chunk) >= self.max_chunks:
                joined_text = '\n'.join(current_chunk)
                chunks.append(joined_text[:-self.overlap_size])
                overlap_text = joined_text[-self.overlap_size:]
                current_chunk = [overlap_text]
                current_length = len(overlap_text)

        if current_chunk:
            joined_text = '\n'.join(current_chunk)
            if joined_text.strip():
                chunks.append(joined_text)

        return chunks

    def split_texts(self, texts: List[str]) -> List[str]:
        chunks = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks


if __name__ == "__main__":
    loader = TextFileLoader("data/KingLear.txt")
    loader.load()
    splitter = CharacterTextSplitter()
    chunks = splitter.split_texts(loader.documents)
    print(len(chunks))
    print(chunks[0])
    print("--------")
    print(chunks[1])
    print("--------")
    print(chunks[-2])
    print("--------")
    print(chunks[-1])
