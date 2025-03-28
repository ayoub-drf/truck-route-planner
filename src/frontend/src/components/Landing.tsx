const Landing = () => {
  return (
    <div className="flex flex-col lg:flex-row items-center justify-between mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-44 gap-8">
      {/* Text Section */}
      <div className="max-w-2xl text-center lg:text-left">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#219596]">
          🚛 Smart Truck Planner – Drive Smarter, Stop Better!
        </h2>
        <p className="mt-4 text-lg text-gray-600">
          Plan your routes like a pro with{" "}
          <span className="font-semibold text-red-400">
            Smart Truck Planner
          </span>{" "}
          – the ultimate tool designed for US truck drivers. Optimize fuel
          stops, rest breaks, and driving hours effortlessly while staying
          compliant with DOT regulations.
          <br />
          <span className="font-semibold text-red-900">
            Less stress, more miles, and smarter stops. Start planning today!
          </span>
        </p>
        <button className="mt-6 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg shadow-md hover:bg-blue-700 transition">
          Get Started
        </button>
      </div>

      {/* Image Section */}
      <div className="flex justify-center">
        <img
          className="w-[1000px] h-auto rounded-lg shadow-lg"
          src="https://wallpapers.com/images/featured/transport-truck-png-ps2y1soxeubelorp.jpg"
          alt="Truck on road"
        />
      </div>
    </div>
  );
};

export default Landing;
