from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/page-tab", response_class=HTMLResponse)
async def page_tab(request: Request):
    # Contenido HTML que se mostrará en la pestaña de Facebook
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mi App de Facebook</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <div style="text-align: center; padding: 20px;">
            <h1>¡Bienvenido a mi aplicación!</h1>
            <p>Esta es una pestaña de página de Facebook para la integración con Meta API.</p>
            <!-- Aquí puedes añadir más contenido, botones, formularios, etc. -->
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)