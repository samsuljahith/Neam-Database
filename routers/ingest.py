import json
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from models.schemas import IngestRequest
from pipeline.file_parser import FileParser

router = APIRouter(tags=["ingest"])

file_parser = FileParser()

@router.post("/ingest")
def ingest(req: IngestRequest, request: Request):
    try:
        return request.app.state.processor.ingest(
            req.collection, req.text,
            req.source, req.metadata)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    collection: str = Form(...),
    metadata: str = Form(None),
):
    """Upload a file to be chunked, embedded, and stored."""
    try:
        ext = "." + file.filename.rsplit(".", 1)[-1].lower()
        if ext not in FileParser.SUPPORTED:
            raise HTTPException(
                400,
                detail=f"Unsupported file type: {ext}. "
                       f"Supported: {', '.join(FileParser.SUPPORTED)}")

        content = await file.read()
        text = file_parser.parse(file.filename, content)

        meta = json.loads(metadata) if metadata else None

        result = request.app.state.processor.ingest(
            collection=collection,
            text=text,
            source=file.filename,
            metadata=meta)

        result["filename"] = file.filename
        result["text_length"] = len(text)
        return result

    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(400, detail="Invalid metadata JSON")
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@router.delete("/documents")
def delete_document(collection: str, source: str, request: Request):
    try:
        return request.app.state.processor.delete_source(
            collection, source)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
