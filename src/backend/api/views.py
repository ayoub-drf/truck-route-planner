from rest_framework import status
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView


class GenerateRouteAPI(APIView):
    def post(self, request):
        data = request.data
        current_location = data.get('currentLocation')
        pickup_location = data.get('pickupLocation')
        dropoff_location = data.get('dropoffLocation')
                
        return Response({
            'message': 'Form submitted successfully',
            'current_location': current_location,
            'pickupLocation': pickup_location,
            'dropoffLocation': dropoff_location
        }, status=status.HTTP_201_CREATED)



@api_view(["GET"])
def place_autocomplete(request):
    query = request.GET.get("query", "")
    if not query:
        return Response({"error": "Query parameter is required"}, status=400)

    url = f"https://api.openrouteservice.org/geocode/autocomplete?api_key={settings.OPENROUTESERVICE_API_KEY}&text={query}"

    response = requests.get(url)
    data = response.json()

    return Response(data['features'], status.HTTP_200_OK)



