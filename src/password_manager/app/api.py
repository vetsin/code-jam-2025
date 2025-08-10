from fastapi import APIRouter, Depends, Request, Response

from ..backend.database import get_vault_storage

router = APIRouter(prefix="/api")

@router.get("/vaults/{vault_id}")
async def load_vault(vault_id: str, storage: get_vault_storage = Depends()):
    return Response(content=storage.read(vault_id), media_type="binary/octet")
    #return VaultService(storage).load_vault(vault_id)

@router.post("/vaults/{vault_id}")
async def save_vault(request: Request, vault_id: str, storage: get_vault_storage = Depends()):
    #body = await request.body()
    # TODO: validate we *can* write it...
    # likely we will have it signed and validate that they wrote it... somehow...
    # https://en.wikipedia.org/wiki/Zero-knowledge_proof
    # we will likely need to store a secret server-side on first-write
    # alternatively we ensure that every vault has an internal randomly generated
    # private key we can use for challenge-response?
    return {"success": False}
    #return VaultService(storage).load_vault(vault_id)
