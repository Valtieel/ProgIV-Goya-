from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    # Primero llamamos al manejador por defecto de DRF, para que siga resolviendo
    # los casos que ya sabe manejar (400, 404, 403, etc.)
    response = exception_handler(exc, context)

    if response is not None:
        # Envolvemos la respuesta en un formato propio y consistente
        response.data = {
            "error": True,
            "detail": response.data,
        }
        return response

    # Si exception_handler no supo qué hacer (típicamente un bug nuestro, no un
    # error de validación de datos), devolvemos manualmente un 500 con el mismo formato
    return Response(
        {"error": True, "detail": "Error interno del servidor."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )