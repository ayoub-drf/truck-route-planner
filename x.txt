import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import polyline from '@mapbox/polyline';
import 'leaflet/dist/leaflet.css';
import '../App.css';

const MapBounds: React.FC<{ bounds: L.LatLngBounds }> = ({ bounds }) => {
  const map = useMap();
  useEffect(() => {
    map.fitBounds(bounds);
  }, [bounds, map]);
  return null;
};

interface StepMarker {
  position: [number, number];
  label: number;
  instruction: string;
}

const RouteMap = () => {
  let markerPosition;
  const [routeLatLngs, setRouteLatLngs] = useState<[number, number][]>([]);
  const [stepMarkers, setStepMarkers] = useState<StepMarker[]>([]);
  const [routeData, setRouteData] = useState<any>(null);

  useEffect(() => {
    let markerPosition;
    fetch('rout-map.json')
      .then(response => response.json())
      .then(data => {
        setRouteData(data);
        const decodedCoords = data.routes[0].geometry;
        setRouteLatLngs(decodedCoords);

        let counter = 1;
        const markers: StepMarker[] = [];
        data.routes[0].segments.forEach((segment: any) => {
          segment.steps.forEach((step: any) => {
            const startIdx = step.way_points[0];
            if (step.stop_coord && step.instruction.toLowerCase().includes('drop')) {
              markerPosition = step.stop_coord;
            }
             else {
              markerPosition = decodedCoords[step.way_points[0]];
            }
            console.log()
            markers.push({
              position: markerPosition,
              // position: decodedCoords[startIdx],
              label: counter,
              instruction: step.instruction,
            });
            counter++;
          });
        });
        setStepMarkers(markers);
      })
      .catch(error => console.error('Error fetching route data:', error));
  }, []);

  let bounds: L.LatLngBounds | undefined;
  if (routeLatLngs.length > 0) {
    bounds = L.latLngBounds(routeLatLngs);
  }

  return (
    <MapContainer center={[34.0, -7.0]} zoom={8} style={{ height: '600px', width: '100%' }}>
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {routeLatLngs.length > 0 && <Polyline positions={routeLatLngs} color="red" />}
      {stepMarkers.map((marker, index) => {
        const icon = L.divIcon({
          className: 'custom-step-icon',
          html: marker.label.toString(),
          iconSize: [24, 24],
          iconAnchor: [12, 12],
        });
        return (
          <Marker key={index} position={marker.position} icon={icon}>
            <Tooltip direction="top" offset={[0, -10]} opacity={1} permanent={false}>
              {marker.instruction}
            </Tooltip>
          </Marker>
        );
      })}
      {bounds && <MapBounds bounds={bounds} />}
    </MapContainer>
  );
};

export default RouteMap;
