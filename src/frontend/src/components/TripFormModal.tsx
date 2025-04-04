/* eslint-disable @typescript-eslint/no-explicit-any */
import { XMarkIcon } from "@heroicons/react/24/solid";
import type { TripFormModalProps } from "../types/types";
import React, { FC, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import api from "../api";
import { toast } from "react-toastify";
import { useRoadStatisticsStore } from "../store/Store";


interface SuggestionsTypes {
  coordinates?: [number, number]
  label: string;
}

const TripFormModal: FC<TripFormModalProps> = ({ hideTripModal, showRouteMap }) => {
  const {setLog, setDropoffMiles, setNumberOfBreaks, setNumberOfFueling, setNumberOfOffDuty, setPickupMiles, setTotalDrivingHours, setTotalDrivingMiles, setRoute} = useRoadStatisticsStore()
  const [currentLocation, setCurrentLocation] = useState<SuggestionsTypes | null>(null);
  const [pickupLocation, setPickupLocation] = useState<SuggestionsTypes | null>(null);
  const [dropoffLocation, setDropoffLocation] = useState<SuggestionsTypes | null>(null);

  const [currentLocationSuggestions, setCurrentLocationSuggestions] = useState<SuggestionsTypes[]>([]);
  const [pickupLocationSuggestions, setPickupLocationSuggestions] = useState<SuggestionsTypes[]>([]);
  const [dropoffLocationSuggestions, setDropoffLocationSuggestions] = useState<SuggestionsTypes[]>([]);

  const handleInputChange = async (e: React.ChangeEvent<HTMLInputElement>, field: string) => {
    const value = e.target.value;
    if (value.length > 2) {
      try {
        const res = await api.get(`autocomplete/?query=${value}`)
        if (res.status == 200) {
          const suggestions = res.data.map((item: any) => ({
            label: item.properties.label,
            coordinates: item.geometry.coordinates
          }));
  
          if (field === "currentLocation") {
            setCurrentLocation({label: value});
            setCurrentLocationSuggestions(suggestions);
          } else if (field === "pickupLocation") {
            setPickupLocation({label: value});
            setPickupLocationSuggestions(suggestions);
          } else if (field === "dropoffLocation") {
            setDropoffLocation({label: value});
            setDropoffLocationSuggestions(suggestions);
          }
        }
      } catch (error) {
        console.error("Error fetching location suggestions:", error);
      }
    } else {
      if (field === "currentLocation") {
        setCurrentLocation({label: value});
      } else if (field === "pickupLocation") {
        setPickupLocation({label: value});
      } else if (field === "dropoffLocation") {
        setDropoffLocation({label: value});
      }
    }
  }

  const handleSuggestionClick = (location: SuggestionsTypes, field: string) => {
    if (field === "currentLocation") {
      setCurrentLocation({label: location.label, coordinates: location.coordinates});
      setCurrentLocationSuggestions([])
    }
    if (field === "pickupLocation") {
      setPickupLocation({label: location.label, coordinates: location.coordinates});
      setPickupLocationSuggestions([])
    }
    if (field === "dropoffLocation") {
      setDropoffLocation({label: location.label, coordinates: location.coordinates});
      setDropoffLocationSuggestions([])
    }
  }


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const data = {
      currentLocation,
      pickupLocation,
      dropoffLocation,
    };


    try {
      const res = await api.post(`generate-route/`, data);
      console.log(res.data)
      setDropoffMiles(res.data.dropoff_miles)
      setNumberOfBreaks(res.data.number_of_breaks)
      setNumberOfFueling(res.data.number_of_fueling)
      setNumberOfOffDuty(res.data.number_of_off_duty)
      setPickupMiles(res.data.pickup_miles)
      setTotalDrivingHours(res.data.total_driving_hours)
      setTotalDrivingMiles(res.data.total_driving_miles)
      setRoute(res.data.route)
      setLog(res.data.log)
      showRouteMap()
      hideTripModal()
    } catch (error: any) {
      toast.warning(error.response.data.message)
    } 

  }

    return (
      <AnimatePresence>
        <motion.div 
          initial={{ opacity: 0, y: 200 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="fixed inset-0 flex justify-center items-center z-[1000]">
          {/* Modal Content */}
          <div className="bg-[#161817] border border-[#ccc] text-white rounded-lg p-6 w-full max-w-md shadow-lg">
            {/* Modal Header */}
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Enter Trip Details</h2>
              <button
                onClick={hideTripModal}
                className="text-gray-500 cursor-pointer hover:text-gray-700"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
  
            {/* Form */}
            <form className="relative" onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="block text-sm font-medium">Current Location</label>
                <input
                  required
                  type="text"
                  value={currentLocation?.label || ""}
                  onChange={(e) => handleInputChange(e, "currentLocation")}
                  placeholder="Enter current location"
                  className="mt-1 w-full border p-2 outline-none focus:border focus:border-[#2186F3] "
                />
                {currentLocationSuggestions.length > 0 && (
                    <ul className="absolute space-y-4 left-0 w-[100%] p-3 border border-t-0 border-[#2186F3] bg-white text-black overflow-y-auto h-full">
                      {currentLocationSuggestions.map((suggestion, index) => (
                        <li
                          key={index}
                          className="flex gap-5 items-center cursor-pointer hover:text-[#2196F3]"
                          onClick={() => handleSuggestionClick(suggestion, "currentLocation")}
                        >
                          <img width={18} height={18} src="https://cdn-icons-png.flaticon.com/512/2875/2875433.png" alt="" />
                          <span>{suggestion.label}</span>
                        </li>
                      ))}
                    </ul>
                )}
              </div>
  
              <div className="mb-3">
                <label className="block text-sm font-medium">Pickup Location</label>
                <input
                  required
                  type="text"
                  value={pickupLocation?.label || ""}
                  onChange={(e) => handleInputChange(e, "pickupLocation")}
                  placeholder="Enter pickup location"
                  className="mt-1 w-full rounded border p-2 outline-none focus:ring-2 focus:ring-blue-500"
                />
                {pickupLocationSuggestions.length > 0 && (
                    <ul className="absolute space-y-4 left-0 w-[100%] p-3 border border-t-0 border-[#2186F3] bg-white text-black overflow-y-auto h-full">
                      {pickupLocationSuggestions.map((suggestion, index) => (
                        <li
                          key={index}
                          className="flex gap-5 items-center cursor-pointer hover:text-[#2196F3]"
                          onClick={() => handleSuggestionClick(suggestion, "pickupLocation")}
                        >
                          <img width={18} height={18} src="https://cdn-icons-png.flaticon.com/512/2875/2875433.png" alt="" />
                          <span>{suggestion.label}</span>
                        </li>
                      ))}
                    </ul>
                )}
              </div>
  
              <div className="mb-3">
                <label className="block text-sm font-medium">Dropoff Location</label>
                <input
                  required
                  type="text"
                  value={dropoffLocation?.label || ""}
                  onChange={(e) => handleInputChange(e, "dropoffLocation")}
                  placeholder="Enter dropoff location"
                  className="mt-1 w-full rounded border p-2 outline-none focus:ring-2 focus:ring-blue-500"
                />
                {dropoffLocationSuggestions.length > 0 && (
                    <ul className="absolute space-y-4 left-0 w-[100%] p-3 border border-t-0 border-[#2186F3] bg-white text-black overflow-y-auto h-full">
                      {dropoffLocationSuggestions.map((suggestion, index) => (
                        <li
                          key={index}
                          className="flex gap-5 items-center cursor-pointer hover:text-[#2196F3]"
                          onClick={() => handleSuggestionClick(suggestion, "dropoffLocation")}
                        >
                          <img width={18} height={18} src="https://cdn-icons-png.flaticon.com/512/2875/2875433.png" alt="" />
                          <span>{suggestion.label}</span>
                        </li>
                      ))}
                    </ul>
                )}
              </div>
  
              <div className="mb-4">
                <label className="block text-sm font-medium">
                  Current Cycle Used (Hrs)
                </label>
                <input
                  required
                  type="number"
                  placeholder="Enter hours"
                  className="mt-1 w-full rounded border p-2 outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
  
              {/* Submit Button */}
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
              >
                Generate Route & ELD Logs
              </button>
            </form>
          </div>
        </motion.div>
      </AnimatePresence>
    );
};


export default TripFormModal;


