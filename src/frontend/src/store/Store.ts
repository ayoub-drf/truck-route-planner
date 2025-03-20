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
