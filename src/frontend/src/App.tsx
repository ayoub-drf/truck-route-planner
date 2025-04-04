import Navbar from "./components/Navbar";
import RouteMap from "./components/RouteMap";
import TripFormModal from "./components/TripFormModal";
import { useTripFormModalStore, useRouteMapStore } from "./store/Store"
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";


const App = () => {
  const { isOpen, hideTripModal } = useTripFormModalStore();
  const { showRouteMap } = useRouteMapStore();

  
  return (
    <div>
      {isOpen && <TripFormModal hideTripModal={hideTripModal} showRouteMap={showRouteMap} />}
      <Navbar />
      <ToastContainer />
      <RouteMap  /> 
    </div>
  );
};

export default App;
