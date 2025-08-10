import logging
from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from pydantic import BaseModel

from password_manager.backend.database import ServerSideVault, get_vault_storage
from password_manager.util.exceptions import VaultReadError, VaultSaveError, VaultValidationError

router = APIRouter(prefix="/api")
logger = logging.getLogger()

@router.get('/health')
async def get_health() -> dict[str, str]:
    return {'status': 'ok'}

@router.get("/vaults/{vault_id}", status_code=status.HTTP_200_OK)
async def load_vault(vault_id: str, storage: get_vault_storage = Depends()) -> Response:
    try:
        server_vault: ServerSideVault = storage.read(vault_id)
        return Response(content=server_vault.vault_data, media_type="binary/octet")
    except VaultReadError as e:
        logger.error("Failed to read vault: {%s}", e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

@router.patch("/vaults/{vault_id}", status_code=status.HTTP_200_OK)
async def save_vault(request: Request, vault_id: str, storage: get_vault_storage = Depends()) -> None:
    try:
        # should throw if signature is invalid
        storage.write(vault_id, await request.body())
    except VaultReadError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    except VaultValidationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from e
    except VaultSaveError as e:
        logger.error("Failed to write vault: {%s}", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

@router.post("/vaults/{vault_id}", status_code=status.HTTP_201_CREATED)
async def new_vault(vault_id: str, storage: get_vault_storage = Depends()) -> ServerSideVault:
    if storage.exists(vault_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vault already exists")
    return storage.create(vault_id)
