from fastapi import APIRouter, HTTPException, Request
from models.schemas import CreateCollectionRequest

router = APIRouter(prefix="/collections", tags=["collections"])

@router.post("")
def create_collection(req: CreateCollectionRequest, request: Request):
    try:
        request.app.state.vector_store.create_collection(req.name)
        return {"message": f"Created: {req.name}"}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@router.delete("/{name}")
def delete_collection(name: str, request: Request):
    try:
        return request.app.state.processor.delete_collection(name)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))

@router.get("")
def list_collections(request: Request):
    collections = request.app.state.metadata_store.list_collections()
    return {"collections": collections}
