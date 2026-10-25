import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Hay que inicializar Django ANTES de importar core.routing (que importa los consumers
# y, por lo tanto, modelos). Si se invierte el orden: AppRegistryNotReady.
# Por eso estos imports quedan "en el medio" del archivo, contra la costumbre.
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import core.routing

# ProtocolTypeRouter es el "portero": según el tipo de conexión decide a dónde va
application = ProtocolTypeRouter({
    # HTTP normal: va al Django de siempre, con todo lo que ya construimos
    "http": django_asgi_app,
    # WebSocket: va al enrutador de Channels. AuthMiddlewareStack completa
    # self.scope["user"] (por ahora desde la sesión; en la Clase 10 sumamos JWT).
    "websocket": AuthMiddlewareStack(
        URLRouter(core.routing.websocket_urlpatterns)
    ),
})