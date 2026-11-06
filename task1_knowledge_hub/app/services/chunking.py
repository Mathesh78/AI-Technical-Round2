from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(value: str, size: int = 500, overlap: int = 100) -> list[str]:
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("Invalid chunk parameters")
    normalized = " ".join(value.split())
    if not normalized:
        return []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    return splitter.split_text(normalized)
