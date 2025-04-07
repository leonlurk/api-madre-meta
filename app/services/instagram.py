import requests
from fastapi import HTTPException
from app.config import settings

class InstagramService:
    """Servicio para manejar las interacciones con la API de Instagram"""
    
    @staticmethod
    async def get_user_profile(access_token):
        """
        Obtiene la información del perfil del usuario
        """
        url = "https://graph.instagram.com/me"
        params = {
            "fields": "id,username",
            "access_token": access_token
        }
        
        try:
            response = requests.get(url, params=params)
            print(f"[DEBUG] Respuesta de Instagram (Perfil): Status={response.status_code}, Contenido={response.text}")
            
            if response.status_code != 200:
                print(f"[ERROR] Error en la respuesta de Instagram: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Error al obtener perfil de usuario: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al obtener información del perfil: {str(e)}")
    
    @staticmethod
    async def get_user_media(access_token, limit=25):
        """
        Obtiene las publicaciones recientes del usuario
        """
        url = "https://graph.instagram.com/me/media"
        params = {
            "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username",
            "access_token": access_token,
            "limit": limit
        }
        
        try:
            response = requests.get(url, params=params)
            print(f"[DEBUG] Respuesta de Instagram (Media): Status={response.status_code}, Contenido={response.text}")
            
            if response.status_code != 200:
                print(f"[ERROR] Error en la respuesta de Instagram: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Error al obtener medios del usuario: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al obtener publicaciones: {str(e)}")
    
    @staticmethod
    async def get_long_lived_token(short_lived_token):
        """
        Intercambia un token de corta duración por uno de larga duración
        """
        url = "https://graph.instagram.com/access_token"
        params = {
            "grant_type": "ig_exchange_token",
            "client_secret": settings.META_APP_SECRET,
            "access_token": short_lived_token
        }
        
        try:
            response = requests.get(url, params=params)
            print(f"[DEBUG] Respuesta de Instagram (Token Larga Duración): Status={response.status_code}, Contenido={response.text}")
            
            if response.status_code != 200:
                print(f"[ERROR] Error en la respuesta de Instagram: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Error al obtener token de larga duración: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al obtener token de larga duración: {str(e)}")