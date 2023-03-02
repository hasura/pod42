"""Load markdown, html, text from files, clean up, split, ingest into Pinecone."""
import tiktoken
import pinecone

from langchain.document_loaders import ReadTheDocsLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import NLTKTextSplitter
from langchain.vectorstores.pinecone import Pinecone


def ingest_docs():
    """Get documents from web pages."""
    loader = ReadTheDocsLoader("langchain.readthedocs.io/en/latest/")
    raw_documents = loader.load()
    text_splitter = NLTKTextSplitter.from_tiktoken_encoder(
        chunk_size=800,
        chunk_overlap=400,
    )
    documents = text_splitter.split_documents(raw_documents)
    embeddings = OpenAIEmbeddings()
    pinecone.init(
        api_key="YOUR_API_KEY",  # find at app.pinecone.io
        environment="YOUR_ENV"  # next to api key in console
    )
    Pinecone.from_documents(documents, embeddings)


if __name__ == "__main__":
    ingest_docs()
