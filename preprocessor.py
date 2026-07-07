def chunk_text(text, max_chars=4000,overlap=400):
    """
    Slices text into smaller segments using an overlapping sliding window

    The overlap buffer ensures that code syntax or complete statements severed at the end of one chunk remain readable at the beginning of next.
    """
    chunks = []
    start = 0
    text_len = len(text)

    if text_len <= max_chars:
        return [text]
    
    while start< text_len:
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk)

        start += (max_chars - overlap)
    
    return chunks

def preprocess_repository_assets(raw_assets):
    """
    Iterates through repository assets to apply text chunking on long source payloads.

    Normalizes file objects into contextual segments tracking their specific slice ID.
    """
    preprocessed_portfolio = []

    for asset in raw_assets:
        path = asset.get("path","unknown_path")
        file_type = asset.get("type","blob")

        if file_type == "blob" and "content" in asset:
            raw_content = asset["content"]

            content_chunks = chunk_text(raw_content,max_chars=4000,overlap=400)

            for index, chunk_slice in enumerate(content_chunks):
                preprocessed_portfolio.append({
                    "path":path,
                    "chunk_id": f"{index + 1}/{len(content_chunks)}",
                    "content": chunk_slice
                })

        else:
            preprocessed_portfolio.append(asset)

    
    return preprocessed_portfolio