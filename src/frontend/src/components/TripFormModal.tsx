/* eslint-disable @typescript-eslint/no-explicit-any */
import { XMarkIcon } from "@heroicons/react/24/solid";
import type { TripFormModalProps } from "../types/types";
import React, { FC, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from 'axios';

interface SuggestionsTypes {
  coordinates?: [number, number]
  label: string;
}

const TripFormModal: FC<TripFormModalProps> = ({ hideTripModal }) => {
  const [currentLocation, setCurrentLocation] = useState<SuggestionsTypes | null>(null);
  const [pickupLocation, setPickupLocation] = useState<SuggestionsTypes | null>(null);
  const [dropoffLocation, setDropoffLocation] = useState<SuggestionsTypes | null>(null);

  const [currentLocationSuggestions, setCurrentLocationSuggestions] = useState<SuggestionsTypes[]>([]);
  const [pickupLocationSuggestions, setPickupLocationSuggestions] = useState<SuggestionsTypes[]>([]);
  const [dropoffLocationSuggestions, setDropoffLocationSuggestions] = useState<SuggestionsTypes[]>([]);

  const mockApi = (query: string): { label: string; coordinates: number[] }[] => {
    const mockLocations = [
      {
        label: "New York, NY, USA",
        coordinates: [-73.9708, 40.68295],
      },
      {
        label: "San Francisco, CA, USA",
        coordinates: [-122.431272, 37.778008],
      },
      {
        label: "Miami-Dade County, FL, USA",
        coordinates: [-80.490594, 25.61606],
      },
    ];
  
    const result = mockLocations.filter((location) =>
      location.label.toLowerCase().includes(query.toLowerCase())
    );
  
    return result;
  };
  
  // const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>, field: string) => {
  //   const value = e.target.value;
  
  //   if (field === "currentLocation") {
  //     setCurrentLocation({label: value});
  //     setCurrentLocationSuggestions(value.length > 2 ? mockApi(value) : []);
  //   } else if (field === "pickupLocation") {
  //     setPickupLocation({label: value});
  //     setPickupLocationSuggestions(value.length > 2 ? mockApi(value) : []);
  //   } else if (field === "dropoffLocation") {
  //     setDropoffLocation({label: value});
  //     setDropoffLocationSuggestions(value.length > 2 ? mockApi(value) : []);
  //   }
  // };

  

  const handleInputChange = async (e: React.ChangeEvent<HTMLInputElement>, field: string) => {
    const value = e.target.value;
    
    if (value.length > 2) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/autocomplete/?query=${value}`);
        const data = await response.json();
        const suggestions = data.map((item: any) => ({
          label: item.properties.label,
          coordinates: item.geometry.coordinates
        }));

        console.log(suggestions)
  
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
      } catch (error) {
        console.error("Error fetching location suggestions:", error);
      }
    } else {
      if (field === "currentLocation") {
        setCurrentLocation({label: value});
        setCurrentLocationSuggestions([]);
      } else if (field === "pickupLocation") {
        setPickupLocation({label: value});
        setPickupLocationSuggestions([]);
      } else if (field === "dropoffLocation") {
        setDropoffLocation({label: value});
        setDropoffLocationSuggestions([]);
      }
    }
  };
  

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
  };
 
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const data = {
      currentLocation,
      pickupLocation,
      dropoffLocation,
    };

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/generate-route/', data);
    
    if (response.status === 200) {
      console.log(response.data)
      console.log('Form submitted successfully');
    } else {
      console.error('Form submission failed');
    }
    } catch (error) {
      console.error('Error submitting form:', error);
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
                  <ul className="absolute space-y-4 left-0 w-[100%] p-3 border border-t-0 border-[#2186F3] bg-white text-black">
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
                  <ul className="absolute space-y-4 left-0 w-[100%] p-3 border border-t-0 border-[#2186F3] bg-white text-black">
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
                  <ul className="absolute space-y-4 left-0 w-[100%] p-3 border border-t-0 border-[#2186F3] bg-white text-black">
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
                value={"20"}
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


