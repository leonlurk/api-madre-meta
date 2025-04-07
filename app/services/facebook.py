import requests
from fastapi import HTTPException
from app.config import settings

class FacebookService:
    """Servicio para manejar las interacciones con la API de Facebook Graph"""
    
    @staticmethod
    async def get_user_info(access_token):
        """
        Obtiene información básica del usuario de Facebook
        """
        url = "https://graph.facebook.com/v18.0/me"
        params = {
            "fields": "id,name,email",
            "access_token": access_token
        }
        
        try:
            response = requests.get(url, params=params)
            print(f"[DEBUG] Respuesta de Facebook (Usuario): Status={response.status_code}, Contenido={response.text}")
            
            if response.status_code != 200:
                print(f"[ERROR] Error en la respuesta de Facebook: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Error al obtener información del usuario: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al obtener información del usuario: {str(e)}")
    
    @staticmethod
    async def get_user_pages(access_token):
        """
        Obtiene las páginas de Facebook que administra el usuario
        """
        url = "https://graph.facebook.com/v18.0/me/accounts"
        params = {
            "access_token": access_token,
            "fields": "id,name,access_token,category"
        }
        
        try:
            response = requests.get(url, params=params)
            print(f"[DEBUG] Respuesta de Facebook (Páginas): Status={response.status_code}, Contenido={response.text}")
            
            if response.status_code != 200:
                print(f"[ERROR] Error en la respuesta de Facebook: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.RequestException as e:
            print(f"[ERROR] Error al obtener páginas: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al obtener páginas: {str(e)}")
    
    @staticmethod
    async def get_pages_instagram_accounts(access_token, pages):
        """
        Para cada página, obtiene la cuenta de Instagram Business asociada
        """
        pages_with_instagram = []
        
        for page in pages:
            page_id = page.get("id")
            page_token = page.get("access_token")
            
            url = f"https://graph.facebook.com/v18.0/{page_id}"
            params = {
                "fields": "instagram_business_account{id,username,profile_picture_url}",
                "access_token": page_token
            }
            
            try:
                response = requests.get(url, params=params)
                print(f"[DEBUG] Respuesta de Facebook (Instagram de página {page_id}): Status={response.status_code}, Contenido={response.text}")
                
                if response.status_code == 200:
                    instagram_data = response.json().get("instagram_business_account")
                    
                    # Agregar información de la página y su cuenta de Instagram
                    pages_with_instagram.append({
                        "page_id": page_id,
                        "page_name": page.get("name"),
                        "page_category": page.get("category"),
                        "page_token": page_token,
                        "instagram_account": instagram_data
                    })
                else:
                    # Si hay error, agregar la página sin información de Instagram
                    pages_with_instagram.append({
                        "page_id": page_id,
                        "page_name": page.get("name"),
                        "page_category": page.get("category"),
                        "page_token": page_token,
                        "instagram_account": None,
                        "error": f"No se pudo obtener información de Instagram: {response.text}"
                    })
                    
            except requests.RequestException as e:
                print(f"[ERROR] Error al obtener Instagram de página {page_id}: {str(e)}")
                # Si hay excepción, agregar la página con el error
                pages_with_instagram.append({
                    "page_id": page_id,
                    "page_name": page.get("name"),
                    "page_token": page_token,
                    "instagram_account": None,
                    "error": f"Error: {str(e)}"
                })
                
        return pages_with_instagram
    
    @staticmethod
    async def get_instagram_messages(page_id, page_token):
        """
        Obtiene los mensajes de Instagram para una página específica
        """
        url = f"https://graph.facebook.com/v18.0/{page_id}/conversations"
        params = {
            "fields": "participants,messages{message,from,to,created_time}",
            "access_token": page_token,
            "platform": "instagram"
        }
        
        try:
            response = requests.get(url, params=params)
            print(f"[DEBUG] Respuesta de Facebook (Mensajes): Status={response.status_code}, Contenido={response.text}")
            
            if response.status_code != 200:
                print(f"[ERROR] Error en la respuesta de Facebook: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Error al obtener mensajes: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al obtener mensajes: {str(e)}")
    
    @staticmethod
    async def send_instagram_message(page_id, recipient_id, message, page_token):
        """
        Envía un mensaje a un usuario de Instagram
        """
        url = f"https://graph.facebook.com/v18.0/{page_id}/messages"
        payload = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message
            },
            "access_token": page_token
        }
        
        try:
            response = requests.post(url, json=payload)
            print(f"[DEBUG] Respuesta de Facebook (Envío de mensaje): Status={response.status_code}, Contenido={response.text}")
            
            if response.status_code != 200:
                print(f"[ERROR] Error en la respuesta de Facebook: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Error al enviar mensaje: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al enviar mensaje: {str(e)}")

        # Implementación futura para instagram_content_publish
 # async def publish_instagram_content(instagram_account_id, image_url, caption, page_token):
 #   """
 #   Publica contenido en Instagram Business
 #   """
 #   url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media"
 #   # Primero crear container de media
 #   media_params = {
 #       "image_url": image_url,
 #       "caption": caption,
 #       "access_token": page_token
 #   }
    
    # Luego publicar el contenido usando el container
    # publish_url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media_publish"
    # ...


    # Implementación futura para instagram_manage_comments
    #    """
    #    Flujo de gestión de comentarios:
    #    1. Obtener comentarios de publicaciones
    #    - GET /{media-id}/comments
    #    
    #    2. Responder a comentarios
    #    - POST /{comment-id}/replies
        
    #    3. Moderar comentarios
    #    - DELETE /{comment-id} (para eliminar)
    #    - HIDE/UNHIDE /{comment-id} (para ocultar/mostrar)

    #        Beneficio: Gestión centralizada de interacciones con clientes
    #    """