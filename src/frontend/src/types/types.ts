export type TripFormModalProps = {
    hideTripModal: () => void;
    showRouteMap: () => void;
    
};

export type RouteMapProps = {
    showRouteMap: () => void;
};

export interface StepMarker {
    position: [number, number];
    label: number;
    instruction: string;
}