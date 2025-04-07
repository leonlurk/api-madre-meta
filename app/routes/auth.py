import os
import requests
from fastapi import APIRouter, Request
from app.config import settings
from app.services.instagram import InstagramService
from app.services.facebook import FacebookService

router = APIRouter()

# Verificar que las variables de entorno estén configuradas
if not settings.META_APP_ID or not settings.META_APP_SECRET or not settings.META_REDIRECT_URI:
    print("[ERROR] Una o más variables de entorno están vacías. Verifica tu .env")

@router.get("/login")
async def login():
    """
    Genera la URL de autorización para Instagram
    """
    auth_url = "https://api.instagram.com/oauth/authorize"
    params = {
        "client_id": settings.META_APP_ID,
        "redirect_uri": settings.META_REDIRECT_URI,
        # Permisos ampliados para acceder a más funcionalidades
        "scope": "instagram_basic,instagram_content_publish,instagram_manage_comments,instagram_manage_messages,pages_messaging,pages_show_list,pages_read_engagement",
        "response_type": "code"
    }
    
    # Construir la URL con los parámetros
    param_string = "&".join([f"{key}={value}" for key, value in params.items()])
    login_url = f"{auth_url}?{param_string}"
    
    return {"login_url": login_url}

@router.get("/callback")
async def auth_callback(request: Request):
    # Verificar qué parámetros llegan
    print(f"[DEBUG] Parámetros recibidos: {request.query_params}")

    # Comprobar si hay un error
    error = request.query_params.get("error")
    if error:
        error_reason = request.query_params.get("error_reason", "desconocido")
        error_description = request.query_params.get("error_description", "Sin descripción")
        return {"error": error, "reason": error_reason, "description": error_description}
    
    # Obtener el código de autorización
    code = request.query_params.get("code")
    if not code:
        return {"error": "No se recibió un código de autorización"}

    # Imprimir valores para verificar que sean correctos
    print(f"[DEBUG] Código recibido: {code}")
    print(f"[DEBUG] Enviando petición a Facebook con redirect_uri: {settings.META_REDIRECT_URI}")

    # Intercambiar el código por un access_token
    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    payload = {
        "client_id": settings.META_APP_ID,
        "client_secret": settings.META_APP_SECRET,
        "redirect_uri": settings.META_REDIRECT_URI,
        "code": code
    }

    try:
        response = requests.get(token_url, params=payload)
        print(f"[DEBUG] Respuesta de Facebook (Token): Status={response.status_code}, Contenido={response.text}")

        if response.status_code != 200:
            return {
                "error": "Fallo en la solicitud de token", 
                "status_code": response.status_code, 
                "response": response.json() if response.content else "Sin respuesta"
            }

        token_data = response.json()
        
        if "access_token" not in token_data:
            return {"error": "No se pudo obtener el token", "response": token_data}
        
        # Obtener token de usuario de Facebook
        fb_user_token = token_data["access_token"]
        
        try:
            # 1. Obtener información del usuario
            user_info = await FacebookService.get_user_info(fb_user_token)
            
            # 2. Obtener las páginas que administra el usuario
            pages = await FacebookService.get_user_pages(fb_user_token)
            
            # 3. Para cada página, obtener los tokens de acceso e información de Instagram Business
            pages_with_instagram = await FacebookService.get_pages_instagram_accounts(fb_user_token, pages)
            
            return {
                "message": "Autenticación exitosa",
                "user_info": user_info,
                "facebook_token": fb_user_token,
                "pages_with_instagram": pages_with_instagram
            }
            
        except Exception as e:
            print(f"[ERROR] Error al procesar información: {str(e)}")
            # Si falla el procesamiento completo, al menos devolver el token básico
            return {
                "message": "Autenticación parcial",
                "facebook_token": fb_user_token,
                "warning": f"No se pudo obtener información completa: {str(e)}"
            }
    
    except requests.RequestException as e:
        return {"error": "Error en la solicitud a Facebook", "details": str(e)}

@router.get("/instagram-login")
async def instagram_basic_login():
    """
    Endpoint alternativo para autenticación básica de Instagram (sin permisos de negocio)
    """
    auth_url = "https://api.instagram.com/oauth/authorize"
    params = {
        "client_id": settings.META_APP_ID,
        "redirect_uri": settings.META_REDIRECT_URI,
        # Solo permisos básicos
        "scope": "user_profile,user_media",
        "response_type": "code"
    }
    
    # Construir la URL con los parámetros
    param_string = "&".join([f"{key}={value}" for key, value in params.items()])
    login_url = f"{auth_url}?{param_string}"
    
    return {"login_url": login_url}

@router.get("/instagram-callback")
async def instagram_auth_callback(request: Request):
    """
    Callback alternativo para autenticación básica de Instagram
    """
    # Verificar qué parámetros llegan
    print(f"[DEBUG] Parámetros recibidos (Instagram básico): {request.query_params}")

    # Comprobar si hay un error
    error = request.query_params.get("error")
    if error:
        error_reason = request.query_params.get("error_reason", "desconocido")
        error_description = request.query_params.get("error_description", "Sin descripción")
        return {"error": error, "reason": error_reason, "description": error_description}
    
    # Obtener el código de autorización
    code = request.query_params.get("code")
    if not code:
        return {"error": "No se recibió un código de autorización"}

    # Intercambiar el código por un access_token (usando la API de Instagram)
    token_url = "https://api.instagram.com/oauth/access_token"
    payload = {
        "client_id": settings.META_APP_ID,
        "client_secret": settings.META_APP_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": settings.META_REDIRECT_URI,
        "code": code
    }

    try:
        response = requests.post(token_url, data=payload)
        print(f"[DEBUG] Respuesta de Instagram: {response.status_code} - {response.text}")

        if response.status_code != 200:
            return {
                "error": "Fallo en la solicitud de token", 
                "status_code": response.status_code, 
                "response": response.json() if response.content else "Sin respuesta"
            }

        token_data = response.json()
        
        if "access_token" not in token_data:
            return {"error": "No se pudo obtener el token", "response": token_data}
        
        # Obtener token de corta duración
        short_lived_token = token_data["access_token"]
        user_id = token_data.get("user_id")
        
        # Obtener token de larga duración
        try:
            long_lived_token = await InstagramService.get_long_lived_token(short_lived_token)
            
            # Obtener información del perfil del usuario
            user_profile = await InstagramService.get_user_profile(long_lived_token.get("access_token"))
            
            return {
                "message": "Autenticación exitosa",
                "short_lived_token": short_lived_token,
                "long_lived_token": long_lived_token,
                "user_id": user_id,
                "profile": user_profile
            }
            
        except Exception as e:
            print(f"[ERROR] Error al procesar token: {str(e)}")
            # Si falla el token de larga duración, al menos devolver el de corta duración
            return {
                "message": "Autenticación exitosa (token básico)",
                "access_token": short_lived_token,
                "user_id": user_id,
                "warning": "No se pudo obtener token de larga duración"
            }
    
    except requests.RequestException as e:
        return {"error": "Error en la solicitud a Instagram", "details": str(e)}