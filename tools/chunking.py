from langchain_text_splitters.character import RecursiveCharacterTextSplitter


def create_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    return splitter.split_text(text)