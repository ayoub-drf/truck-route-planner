/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Polyline,
  Tooltip,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "../App.css";
import { useRoadStatisticsStore } from "../store/Store";

// import type { RouteMapProps } from "../types/types";

const MapBounds: React.FC<{ bounds: L.LatLngBounds }> = ({ bounds }) => {
  const map = useMap();
  useEffect(() => {
    map.fitBounds(bounds);
  }, [bounds, map]);
  return null;
};

interface StepMarker {
  position: [number, number];
  label: string;
  instruction: string;
}

// const RouteMap: FC<RouteMapProps> = ({ showRouteMap }) => {
const RouteMap = () => {
  const {
    dropoffMiles,
    numberOfBreaks,
    numberOfFueling,
    numberOfOffDuty,
    pickupMiles,
    totalDrivingHours,
    totalDrivingMiles,
    route,
  } = useRoadStatisticsStore();
  const [routeLatLngs, setRouteLatLngs] = useState<[number, number][]>([]);
  const [stepMarkers, setStepMarkers] = useState<StepMarker[]>([]);

  useEffect(() => {
    let markerPosition;
    let label: string;
    console.log("hello");
    console.log("dropoffMiles", dropoffMiles);
    console.log("numberOfBreaks", numberOfBreaks);
    console.log("numberOfFueling", numberOfFueling);
    console.log("numberOfOffDuty", numberOfOffDuty);
    console.log("pickupMiles", pickupMiles);
    console.log("totalDrivingHours", totalDrivingHours);
    console.log("totalDrivingMiles", totalDrivingMiles);
    console.log("route", route);

    if (dropoffMiles > 0) {
      const decodedCoords = route.routes[0].geometry;
      setRouteLatLngs(decodedCoords);

      let counter = 1;
      const markers: StepMarker[] = [];
      route.routes[0].segments.forEach((segment: any) => {
        segment.steps.forEach((step: any) => {
          if (step.stop_coord) {
            markerPosition = step.stop_coord;
            if (step.instruction.toLowerCase() == "fueling stop") {
              console.log(step, counter);
              label = "FL";
            } else if (
              step.instruction.toLowerCase() == "off-duty break stop"
            ) {
              console.log(step, counter);
              label = "OF";
            } else if (step.instruction.toLowerCase() == "break stop") {
              console.log(step, counter);
              label = "BR";
            } else if (step.instruction.toLowerCase() == "pickup stop") {
              console.log(step, counter);
              label = "PC";
            } else if (step.instruction.toLowerCase() == "dropoff stop") {
              console.log(step, counter);
              label = "DF";
            }
          } else {
            markerPosition = decodedCoords[step.way_points[0]];
            label = `${counter}`;
          }
          markers.push({
            position: markerPosition,
            label: label,
            instruction: step.instruction,
          });
          counter++;
        });
      });
      setStepMarkers(markers);
    }
  }, [
    dropoffMiles,
    numberOfBreaks,
    numberOfFueling,
    numberOfOffDuty,
    pickupMiles,
    totalDrivingHours,
    totalDrivingMiles,
    route,
  ]);

  let bounds: L.LatLngBounds | undefined;
  if (routeLatLngs.length > 0) {
    bounds = L.latLngBounds(routeLatLngs);
  }

  return (
    <div className="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
      <div
        id="statistics"
        className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 gap-5 my-5 text-black font-bold"
      >
        <div className="flex flex-col justify-around p-6 rounded-md shadow-2xl">
          <div className="flex justify-between items-center mb-4">
            <h3 className="uppercase">Total Driving Hours</h3>
            <img
              width={30}
              src="https://cdn-icons-png.flaticon.com/512/810/810070.png"
              alt=""
            />
          </div>
          <h1 className="text-3xl ">{totalDrivingHours}</h1>
        </div>

        <div className="flex flex-col justify-around p-6 rounded-md shadow-2xl">
          <div className="flex justify-between items-center mb-4">
            <h3 className="uppercase">Total Driving Miles</h3>
            <img
              width={30}
              src="https://cdn-icons-png.flaticon.com/512/1455/1455330.png"
              alt=""
            />
          </div>
          <h1 className="text-3xl ">{totalDrivingMiles}</h1>
        </div>

        <div className="flex flex-col justify-around p-6 rounded-md shadow-2xl">
          <div className="flex justify-between items-center mb-4">
            <h3 className="uppercase">Number of breaks (30M)</h3>
            <img
              width={30}
              src="https://cdn-icons-png.flaticon.com/512/3133/3133310.png"
              alt=""
            />
          </div>
          <h1 className="text-3xl">{numberOfBreaks}</h1>
        </div>

        <div className="flex flex-col justify-around p-6 rounded-md shadow-2xl">
          <div className="flex justify-between items-center mb-4">
            <h3 className="uppercase">Number of Fueling (1000M)</h3>
            <img
              width={30}
              src="https://cdn-icons-png.flaticon.com/512/891/891035.png"
              alt=""
            />
          </div>
          <h1 className="text-3xl">{numberOfFueling}</h1>
        </div>

        <div className="flex flex-col justify-around p-6 rounded-md shadow-2xl">
          <div className="flex justify-between items-center mb-4">
            <h3 className="uppercase">Pick up miles</h3>
            <img
              width={30}
              src="https://cdn-icons-png.flaticon.com/512/9017/9017603.png"
              alt=""
            />
          </div>
          <h1 className="text-3xl">{pickupMiles}</h1>
        </div>

        <div className="flex flex-col justify-around p-6 rounded-md shadow-2xl">
          <div className="flex justify-between items-center mb-4">
            <h3 className="uppercase">Dropoff miles</h3>
            <img
              width={30}
              src="https://cdn-icons-png.flaticon.com/512/9431/9431433.png"
              alt=""
            />
          </div>
          <h1 className="text-3xl">{dropoffMiles}</h1>
        </div>

        <div className="flex flex-col justify-around p-6 rounded-md shadow-2xl">
          <div className="flex justify-between items-center mb-4">
            <h3 className="uppercase">Number of off-duty</h3>
            <img
              width={30}
              src="https://cdn-icons-png.flaticon.com/512/8841/8841259.png"
              alt=""
            />
          </div>
          <h1 className="text-3xl">{numberOfOffDuty}</h1>
        </div>

        <div className="flex flex-col justify-around p-6 rounded-md shadow-2xl bg-green-500 text-white cursor-pointer">
          <div className="flex justify-between items-center mb-4">
            <h3 className="uppercase">Log Sheets (PDF)</h3>
            <img
              width={30}
              src="https://cdn-icons-png.flaticon.com/512/1144/1144698.png"
              alt=""
            />
          </div>
          <h1 className="text-3xl uppercase">click me</h1>
        </div>
      </div>
      <MapContainer
        center={[35.8198995, -83.8869325 ]}
        zoom={5}
        style={{ height: "1000px", width: "100%" }}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {routeLatLngs.length > 0 && (
          <Polyline positions={routeLatLngs} color="red" />
        )}
        {stepMarkers.map((marker, index) => {
          const icon = L.divIcon({
            className: "custom-step-icon",
            html: marker.label.toString(),
            iconSize: [25, 25],
            iconAnchor: [12, 12],
          });

          return (
            <Marker key={index} position={marker.position} icon={icon}>
              <Tooltip
                direction="top"
                offset={[0, -10]}
                opacity={1}
                permanent={false}
              >
                {marker.instruction}
              </Tooltip>
            </Marker>
          );
        })}
        {bounds && <MapBounds bounds={bounds} />}
      </MapContainer>
    </div>
  );
};

export default RouteMap;
