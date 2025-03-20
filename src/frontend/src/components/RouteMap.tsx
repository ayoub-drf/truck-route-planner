import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Tooltip, useMap } from 'react-leaflet';
import type { StepMarker } from "../types/types";
import L from 'leaflet';
import polyline from '@mapbox/polyline';
import 'leaflet/dist/leaflet.css';
import '../App.css';
import axios from 'axios';



const RouteMap = () => {
  const [routeLatLngs, setRouteLatLngs] = useState<[number, number][]>([]);
  const [routeData, setRouteData] = useState<any>(null);
  const [bboxView, setBboxView] = useState<[number, number]>([34.0, -7.0])

  useEffect(() => {
    fetch("rout-map.json").then(res => res.json()).then(data => {
        setRouteData(data)
        const centerView = [
            (data.bbox[1] + data.bbox[3]) / 2,  // Average latitude
            (data.bbox[0] + data.bbox[2]) / 2 // Average longitude
        ];

        // console.log(centerView)





        // Decode the encoded polyline geometry (returns an array of [lat, lng] pairs)
        const decodedCoords = polyline.decode(data.routes[0].geometry);
        setRouteLatLngs(decodedCoords)

        let counter = 1;
        const markers: StepMarker[] = [];

        data.routes[0].segments.forEach(segment => {
            segment.steps.forEach(step => {
                const startIdx = step.way_points[0];
                markers.push({
                    position: decodedCoords[startIdx],
                    label: counter,
                    instruction: step.instruction,
                  });
                counter++;
            });
        });

        // console.log(markers)

    }).catch((error) => console.error('Error fetching route data:', error))
    
  }, [])

  useEffect(() => {
    // console.log(routeData)
  }, [routeData])
  
  

  return (
    // The main container where the map is rendered.
    <MapContainer center={[33.819899500000005, -83.880172]} zoom={5} style={{ height: '600px', width: '100%' }}>
        {/* Loads the background images (tiles) that make up the map */}
        <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Draws a line on the map by connecting a series of coordinates */}
        {routeLatLngs.length > 0 && <Polyline positions={routeLatLngs} color="red" />}

    </MapContainer>
  )
}

export default RouteMap