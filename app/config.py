import os
from dotenv import load_dotenv

# Forzar recarga del archivo .env
load_dotenv(override=True)

class Settings:
    APP_ENV = os.getenv("APP_ENV", "development")
    META_APP_ID = os.getenv("META_APP_ID")
    META_APP_SECRET = os.getenv("META_APP_SECRET")
    META_REDIRECT_URI = os.getenv("META_REDIRECT_URI")
    
    # URLs alternativas
    INSTAGRAM_REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI", META_REDIRECT_URI)
    
    # Configuración del servidor
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    # Opciones de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()
    
    def __str__(self):
        return f"ENV: {self.APP_ENV}, META_REDIRECT_URI: {self.META_REDIRECT_URI}"

settings = Settings()
print(f"Configuración cargada: {settings}")