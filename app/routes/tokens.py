from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.utils.token_utils import TokenUtils

router = APIRouter()

@router.get("/verify")
async def verify_token(token: str = Query(..., description="Token a verificar")):
    """
    Verifica si un token es válido y obtiene información sobre él
    """
    try:
        token_info = await TokenUtils.verify_token(token)
        return token_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/refresh")
async def refresh_token(token: str = Query(..., description="Token de larga duración a refrescar")):
    """
    Refresca un token de larga duración antes de que expire
    """
    try:
        refresh_result = await TokenUtils.refresh_long_lived_token(token)
        return refresh_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/decode")
async def decode_token(token: str = Query(..., description="Token a decodificar (solo para debug)")):
    """
    Muestra información básica de un token (sin verificar su validez)
    """
    try:
        token_info = TokenUtils.decode_token_info(token)
        return token_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))