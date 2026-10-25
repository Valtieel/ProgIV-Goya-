from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # re_path acepta expresiones regulares. (?P<project_id>\d+) captura uno o más dígitos
    # con el nombre project_id, que el consumer lee de self.scope["url_route"]["kwargs"].
    # $ marca el final: ws/projects/1/ coincide, ws/projects/1/otra-cosa/ no.
    # as_asgi() es el equivalente a as_view() de las vistas de Django.
    re_path(r"ws/projects/(?P<project_id>\d+)/$", consumers.TaskNotificationConsumer.as_asgi()),
]