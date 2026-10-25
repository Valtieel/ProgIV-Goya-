from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    # scope conecta esta clase con la entrada "login" de DEFAULT_THROTTLE_RATES
    # (la agregamos al settings.py en la Etapa 2)
    scope = "login"

    def get_cache_key(self, request, view):
        # En el login todavía no hay usuario autenticado, así que el límite
        # se cuenta por IP. El contador vive en la caché de Django, por eso
        # se reinicia si se reinicia el servidor.
        ip = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ip}