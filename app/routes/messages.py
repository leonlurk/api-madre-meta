from fastapi import APIRouter, Depends, HTTPException, Header, Query
from typing import Optional
from app.services.instagram import InstagramService
from app.services.facebook import FacebookService

router = APIRouter()

# ENDPOINTS DE INSTAGRAM BÁSICO (API Original)

async def verify_token(access_token: Optional[str] = Header(None)):
    """
    Verifica que se haya proporcionado un token de acceso
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Token de acceso no proporcionado")
    return access_token

@router.get("/")
async def get_messages(access_token: str = Depends(verify_token)):
    """
    En el futuro, listar mensajes de Instagram
    """
    return {"message": "Endpoint para listar mensajes (en desarrollo)", "token_provided": True}

@router.get("/profile")
async def get_profile(access_token: str = Depends(verify_token)):
    """
    Obtiene el perfil del usuario autenticado
    """
    try:
        user_profile = await InstagramService.get_user_profile(access_token)
        return {"profile": user_profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/media")
async def get_media(access_token: str = Depends(verify_token), limit: int = 10):
    """
    Obtiene las publicaciones recientes del usuario
    """
    try:
        user_media = await InstagramService.get_user_media(access_token, limit)
        return user_media
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ENDPOINTS DE INSTAGRAM BUSINESS (API de Facebook)

async def verify_page_token(page_token: Optional[str] = Header(None, alias="x-page-token")):
    """
    Verifica que se haya proporcionado un token de página
    """
    if not page_token:
        raise HTTPException(status_code=401, detail="Token de página no proporcionado")
    return page_token

@router.get("/instagram")
async def get_instagram_messages(
    page_id: str = Query(..., description="ID de la página de Facebook"),
    page_token: str = Depends(verify_page_token)
):
    """
    Obtiene los mensajes de Instagram para una página específica
    """
    try:
        messages = await FacebookService.get_instagram_messages(page_id, page_token)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instagram/send")
async def send_instagram_message(
    page_id: str = Query(..., description="ID de la página de Facebook"),
    recipient_id: str = Query(..., description="ID del destinatario"),
    message: str = Query(..., description="Texto del mensaje"),
    page_token: str = Depends(verify_page_token)
):
    """
    Envía un mensaje a un usuario de Instagram
    """
    try:
        result = await FacebookService.send_instagram_message(page_id, recipient_id, message, page_token)
        return {
            "success": True,
            "message": "Mensaje enviado correctamente",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ENDPOINTS DE PRUEBA

@router.get("/test-token")
async def test_token():
    """
    Endpoint de prueba que usa directamente el token generado en el panel de Meta
    """
    # Reemplaza esto con el token que generaste en el panel de Meta
    token = "IGAATkAZCUDT9ZABZAFBmdVpNVC1WUzFFVUY2eFJYRXQ5QXFiV2oyVkZAmcnB5ZAEJZAcmFCWTU4TU1QTGFZAN01GbVZArbk9CbFh5OXlFdU5tX255TWV1eHkyMzFkSFVNRTFJWk9TdTdNQzB4Y2JlbjFEeG9QOFkxU0lQVjNwaDltYm8wYwZDZD"
    
    print(f"[DEBUG] Intentando probar con token: {token[:10]}...")
    
    try:
        # Intentar obtener el perfil usando el token
        user_profile = await InstagramService.get_user_profile(token)
        
        # Si funciona, también intentar obtener medios
        try:
            user_media = await InstagramService.get_user_media(token)
            return {
                "success": True,
                "profile": user_profile,
                "media": user_media
            }
        except Exception as e:
            print(f"[ERROR] Fallo al obtener medios: {str(e)}")
            # Si falla al obtener medios, al menos devolver el perfil
            return {
                "success": True,
                "profile": user_profile,
                "media_error": str(e)
            }
            
    except Exception as e:
        print(f"[ERROR] Fallo al obtener perfil: {str(e)}")
        # Si falla todo, devolver error
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/test-graph-api")
async def test_graph_api():
    """
    Endpoint de prueba específico para la API Graph de Instagram
    """
    # Reemplaza con tu token de la API Graph
    token = "IGAATkAZCUDT9ZABZAFBmdVpNVC1WUzFFVUY2eFJYRXQ5QXFiV2oyVkZAmcnB5ZAEJZAcmFCWTU4TU1QTGFZAN01GbVZArbk9CbFh5OXlFdU5tX255TWV1eHkyMzFkSFVNRTFJWk9TdTdNQzB4Y2JlbjFEeG9QOFkxU0lQVjNwaDltYm8wYwZDZD"
    
    try:
        # La API Graph usa endpoints diferentes
        url = "https://graph.facebook.com/v18.0/me"
        params = {
            "fields": "id,name,accounts{instagram_business_account{id,username,profile_picture_url}}",
            "access_token": token
        }
        
        response = requests.get(url, params=params)
        print(f"[DEBUG] Respuesta de Graph API: Status={response.status_code}, Contenido={response.text}")
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Error {response.status_code}: {response.text}"
            }
            
        return {
            "success": True,
            "data": response.json()
        }
            
    except Exception as e:
        print(f"[ERROR] Fallo en API Graph: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/test-business-messages")
async def test_business_messages(
    page_id: str = Query(..., description="ID de la página de Facebook"),
    page_token: str = Query(..., description="Token de acceso de la página")
):
    """
    Endpoint de prueba para probar la obtención de mensajes de Instagram Business
    """
    try:
        messages = await FacebookService.get_instagram_messages(page_id, page_token)
        return {
            "success": True,
            "messages": messages
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }