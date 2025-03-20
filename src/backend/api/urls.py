from django.urls import path
from .views import (
    place_autocomplete,
    GenerateRouteAPI,
)

urlpatterns = [
    path("autocomplete/", place_autocomplete, name="place-autocomplete"),
    path('generate-route/', GenerateRouteAPI.as_view(), name='generate_route'),
]
