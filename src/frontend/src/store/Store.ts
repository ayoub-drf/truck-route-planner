/* eslint-disable @typescript-eslint/no-explicit-any */
import { create } from "zustand";

type TripFormModalStoreType = {
    isOpen: boolean;
    showTripModal: () => void;
    hideTripModal: () => void;
};

export const useTripFormModalStore = create<TripFormModalStoreType>((set) => ({
    isOpen: false,
    showTripModal: () => set({ isOpen: true }),
    hideTripModal: () => set({ isOpen: false }),
}));

type RouteMapStoreType = {
    isRouteMapOpen: boolean;
    showRouteMap: () => void;
    hideRouteMap: () => void;
};

export const useRouteMapStore = create<RouteMapStoreType>((set) => ({
    isRouteMapOpen: false,
    showRouteMap: () => set({ isRouteMapOpen: true }),
    hideRouteMap: () => set({ isRouteMapOpen: false }),
}));

type RoadStatisticsStoreType = {
    log: string,
    dropoffMiles: number,
    numberOfBreaks: number,
    numberOfFueling: number,
    numberOfOffDuty: number,
    pickupMiles: number,
    totalDrivingHours: number,
    totalDrivingMiles: number,
    route: any,
    setDropoffMiles: (x: number) => void,
    setNumberOfBreaks: (x: number) => void,
    setNumberOfFueling: (x: number) => void,
    setNumberOfOffDuty: (x: number) => void,
    setPickupMiles: (x: number) => void,
    setTotalDrivingHours: (x: number) => void,
    setTotalDrivingMiles: (x: number) => void,
    setRoute: (r: any) => void,
    setLog: (l: any) => void,
}

export const useRoadStatisticsStore = create<RoadStatisticsStoreType>((set) => ({
    log: "",
    dropoffMiles: 0,
    numberOfBreaks: 0,
    numberOfFueling: 0,
    numberOfOffDuty: 0,
    pickupMiles: 0,
    totalDrivingHours: 0,
    totalDrivingMiles: 0,
    route: {},
    setDropoffMiles: (x) => set(() => ({ dropoffMiles: x })),
    setNumberOfBreaks: (x) => set(() => ({ numberOfBreaks: x })),
    setNumberOfFueling: (x) => set(() => ({ numberOfFueling: x })),
    setNumberOfOffDuty: (x) => set(() => ({ numberOfOffDuty: x })),
    setPickupMiles: (x) => set(() => ({ pickupMiles: x })),
    setTotalDrivingHours: (x) => set(() => ({ totalDrivingHours: x })),
    setTotalDrivingMiles: (x) => set(() => ({ totalDrivingMiles: x })),
    setRoute: (r) => set(() => ({ route: r })),
    setLog: (l) => set(() => ({ log: l })),
}));