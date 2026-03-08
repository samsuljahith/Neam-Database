import csv
import io
import PyPDF2

SUPPORTED_TYPES = {
    "text/plain": ".txt",
    "application/pdf": ".pdf",
    "text/csv": ".csv",
}


class UnsupportedFileType(ValueError):
    pass


class Parser:
    """Extracts plain text from uploaded file bytes."""

    def parse(self, data: bytes, content_type: str,
              filename: str) -> str:
        ct = content_type.split(";")[0].strip()

        if ct == "text/plain":
            return self._parse_txt(data)
        elif ct == "application/pdf":
            return self._parse_pdf(data)
        elif ct == "text/csv":
            return self._parse_csv(data)
        else:
            # Fall back to extension if browser sends wrong MIME
            ext = filename.rsplit(".", 1)[-1].lower()
            if ext == "txt":
                return self._parse_txt(data)
            elif ext == "pdf":
                return self._parse_pdf(data)
            elif ext == "csv":
                return self._parse_csv(data)
            raise UnsupportedFileType(
                f"Unsupported file type: {content_type}. "
                f"Accepted: .txt, .pdf, .csv"
            )

    def _parse_txt(self, data: bytes) -> str:
        return data.decode("utf-8", errors="replace").strip()

    def _parse_pdf(self, data: bytes) -> str:
        reader = PyPDF2.PdfReader(io.BytesIO(data))
        pages = [
            page.extract_text() or ""
            for page in reader.pages
        ]
        return "\n\n".join(pages).strip()

    def _parse_csv(self, data: bytes) -> str:
        text = data.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        rows = []
        for row in reader:
            # Render each row as "key: value" pairs, one per line
            rows.append(
                ", ".join(
                    f"{k}: {v}" for k, v in row.items() if v
                )
            )
        return "\n".join(rows).strip()
