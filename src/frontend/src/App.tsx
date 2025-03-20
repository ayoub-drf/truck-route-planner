import Navbar from "./components/Navbar";
import RouteMap from "./components/RouteMap";
import TripFormModal from "./components/TripFormModal";
import { useTripFormModalStore } from "./store/Store"


const App = () => {
  const { isOpen, hideTripModal } = useTripFormModalStore();
  
  return (
    <div>
      {isOpen && <TripFormModal hideTripModal={hideTripModal} />}
      <Navbar />
      <RouteMap />
    </div>
  );
};

export default App;
