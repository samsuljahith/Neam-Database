import csv
import io


class FileParser:
    """Extracts text from various file formats."""

    SUPPORTED = {".txt", ".pdf", ".csv"}

    def parse(self, filename: str, content: bytes) -> str:
        """Extract text from file bytes."""
        ext = self._get_extension(filename)

        if ext == ".txt":
            return self._parse_txt(content)
        elif ext == ".pdf":
            return self._parse_pdf(content)
        elif ext == ".csv":
            return self._parse_csv(content)
        else:
            raise ValueError(
                f"Unsupported file type: {ext}. "
                f"Supported: {', '.join(self.SUPPORTED)}")

    def _get_extension(self, filename: str) -> str:
        return "." + filename.rsplit(".", 1)[-1].lower()

    def _parse_txt(self, content: bytes) -> str:
        return content.decode("utf-8")

    def _parse_pdf(self, content: bytes) -> str:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(content))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        if not pages:
            raise ValueError("Could not extract text from PDF")
        return "\n\n".join(pages)

    def _parse_csv(self, content: bytes) -> str:
        text = content.decode("utf-8")
        reader = csv.reader(io.StringIO(text))
        rows = []
        headers = None
        for i, row in enumerate(reader):
            if i == 0:
                headers = row
            else:
                if headers:
                    pairs = [f"{h}: {v}"
                             for h, v in zip(headers, row) if v]
                    rows.append(". ".join(pairs))
                else:
                    rows.append(", ".join(row))
        return "\n".join(rows)
