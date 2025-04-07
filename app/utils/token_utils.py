import json
import time
from datetime import datetime
import requests
from app.config import settings

class TokenUtils:
    """Utilidades para manejo de tokens de autenticación"""
    
    @staticmethod
    def decode_token_info(token):
        """
        Intenta obtener información básica de un token (sin verificar su validez)
        Solo para debugging - no se debe confiar en esta información para validación
        """
        try:
            # Los tokens están codificados en base64, pero no podemos decodificarlos directamente
            # Solo podemos obtener información llamando a la API de debug_token
            return {
                "token_preview": token[:15] + "..." if token else None,
                "length": len(token) if token else 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    async def verify_token(token):
        """
        Verifica si un token es válido y obtiene información sobre él
        """
        url = "https://graph.facebook.com/debug_token"
        params = {
            "input_token": token,
            "access_token": f"{settings.META_APP_ID}|{settings.META_APP_SECRET}"
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json().get('data', {})
                return {
                    "is_valid": data.get('is_valid', False),
                    "app_id": data.get('app_id'),
                    "expires_at": datetime.fromtimestamp(data.get('expires_at', 0)).isoformat() if data.get('expires_at') else None,
                    "scopes": data.get('scopes', []),
                    "type": data.get('type')
                }
            return {"error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    async def refresh_long_lived_token(long_lived_token):
        """
        Refresca un token de larga duración (debe llamarse antes de que expire)
        Los tokens de Instagram de larga duración duran 60 días
        """
        url = "https://graph.instagram.com/refresh_access_token"
        params = {
            "grant_type": "ig_refresh_token",
            "access_token": long_lived_token
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            return {"error": f"Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": str(e)}