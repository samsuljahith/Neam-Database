from config import settings

class Chunker:
    """Splits text into overlapping chunks at natural boundaries."""

    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.overlap = settings.chunk_overlap

    def chunk(self, text: str) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text.strip()] if text.strip() else []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            if end < len(text):
                # Try paragraph break first
                pb = text.rfind("\n\n", start, end)
                if pb > start:
                    end = pb
                else:
                    # Try sentence break
                    for sep in [". ", "! ", "? ", "\n"]:
                        sb = text.rfind(sep, start, end)
                        if sb > start:
                            end = sb + len(sep)
                            break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.overlap if end < len(text) else end

        return chunks
