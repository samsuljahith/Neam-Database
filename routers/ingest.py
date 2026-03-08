from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from models.schemas import IngestRequest
from pipeline.parser import Parser, UnsupportedFileType

router = APIRouter(tags=["ingest"])
parser = Parser()

@router.post("/ingest")
def ingest(req: IngestRequest, request: Request):
    try:
        return request.app.state.processor.ingest(
            req.collection, req.text,
            req.source, req.metadata)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@router.post("/upload")
async def upload(
    request: Request,
    collection: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        data = await file.read()
        text = parser.parse(data, file.content_type, file.filename)
    except UnsupportedFileType as e:
        raise HTTPException(415, detail=str(e))

    if not text:
        raise HTTPException(422, detail="File parsed but contained no text.")

    try:
        result = request.app.state.processor.ingest(
            collection, text,
            source=file.filename)
        result["filename"] = file.filename
        result["parsed_chars"] = len(text)
        return result
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@router.delete("/documents")
def delete_document(collection: str, source: str, request: Request):
    try:
        return request.app.state.processor.delete_source(
            collection, source)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
