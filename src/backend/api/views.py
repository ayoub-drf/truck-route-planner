from django.utils.crypto import get_random_string
from rest_framework import status
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .tasks import (
    create_rests_and_stops,
    draw_log,
    adjust_hours,
)
import requests


DIRECTIONS_URL = settings.DIRECTIONS_URL
OPENROUTESERVICE_AUTOCOMPLETE = settings.OPENROUTESERVICE_AUTOCOMPLETE


class GenerateRouteAPI(APIView):
    def post(self, request):
        data = request.data
        current_location = data.get('currentLocation')
        pickup_location = data.get('pickupLocation')
        dropoff_location = data.get('dropoffLocation')
        currentUsedHours = data.get('currentUsedHours')
        print('currentUsedHours', currentUsedHours)
        print('currentUsedHours', type(currentUsedHours))
        
        route_coordinates = [
            current_location.get('coordinates'),
            pickup_location.get('coordinates'),
            dropoff_location.get('coordinates')
        ]

        body = {
            "coordinates": route_coordinates,
            "options": {"avoid_features": ["ferries"]}  # use just roads
        }

        headers = {
            'Authorization': settings.OPENROUTESERVICE_API_KEY,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(DIRECTIONS_URL, json=body, headers=headers)
            route_data = response.json()
            if route_data.get('error'):
                return Response({'message': route_data['error']['message']}, status=status.HTTP_404_NOT_FOUND)
            
            # print('route_data ', route_data)
            result = create_rests_and_stops(route_data, int(currentUsedHours))
            log_sheet_result = adjust_hours(result['log_sheet_result'])
            log = draw_log(log_sheet_result, f"log_sheet_output-{get_random_string(10)}.pdf")
            
            print('log', log)
            
            total_driving_hours = round((route_data.get('routes')[0].get('summary').get('duration') / 3600), 2)
            total_driving_miles = round((route_data.get('routes')[0].get('summary').get('distance') * 0.000621371), 2)
            
            
            return Response({
                'route': result['result'],
                'number_of_breaks': result['number_of_breaks'],
                'number_of_fueling': result['number_of_fueling'],
                'number_of_off_duty': result['number_of_off_duty'],
                'pickup_miles': result['pickup_miles'],
                'dropoff_miles': total_driving_miles,
                'total_driving_miles': total_driving_miles,
                'total_driving_hours': total_driving_hours,
                'log': log,
            }, status=status.HTTP_201_CREATED)
        except  Exception as e:
            print(e)
            return Response({
                'message': "an error occurred please wait abd try again",
            }, status=status.HTTP_404_NOT_FOUND)
            
                



@api_view(["GET"])
def place_autocomplete(request):
    query = request.GET.get("query", "")
    if not query:
        return Response({"error": "Query parameter is required"}, status=400)

    url = f"{OPENROUTESERVICE_AUTOCOMPLETE}{settings.OPENROUTESERVICE_API_KEY}&text={query}"

    response = requests.get(url)
    data = response.json()

    return Response(data['features'], status.HTTP_200_OK)



