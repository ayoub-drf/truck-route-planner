export type TripFormModalProps = {
    hideTripModal: () => void;
};

export interface StepMarker {
    position: [number, number];
    label: number;
    instruction: string;
}