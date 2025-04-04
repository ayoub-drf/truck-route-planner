import { motion } from "framer-motion";


const Sidebar = () => {
  return (
    <motion.div

    className="w-1/5 h-screen bg-[#191c24]">
      <a href="" className="text-primary block font-extrabold py-4 px-7">
        <i className="fa-solid fa-map-pin mr-2 text-3xl"></i>
        <span className="text-[25px] ">Smart</span>
        <motion.i 
        // initial={{ x: -80, rotate: 180 }}
        // initial={{ x: -133, rotate: 0 }}
        // animate={{ x: 32, rotate: 10 }}
        // animate={{ x: 0, rotate: -180 }}
        // hidden=
        transition={{ type: "tween", duration: 1, repeat: Infinity, repeatType: "reverse" }}
        className="fa-solid fa-truck-moving text-3xl"></motion.i>
      </a>
      <a
        href=""
        className="relative flex w-fit  py-4 px-7 justify-center rounded transition"
      >
        <img
        width={40}
          src="https://media.istockphoto.com/id/610003972/vector/vector-businessman-black-silhouette-isolated.jpg?s=612x612&w=0&k=20&c=Iu6j0zFZBkswfq8VLVW8XmTLLxTLM63bfvI6uXdkacM="
          className="rounded-[50%] mr-3"
          alt=""
        />
        <p className="font-bold ml-1 text-[18px] text-green-700 "> Sign in
            <i className="fa-solid fa-arrow-right-to-bracket ml-2"></i>
        </p>
      </a>
      <div className="mt-6">
        <a href="/" className="flex items-center transition capitalize py-2 rounded-tr-4xl rounded-br-4xl bg-[#000000] text-[#EB1616]  w-[88%] px-7 text-[17px] ">
          <i className="fa fa-tachometer-alt me-2 bg-[#000000] p-3 rounded-[50%] "></i>
          <span>Dashboard</span>
        </a>
        <a href="/" className="flex items-center transition capitalize py-2 rounded-tr-4xl rounded-br-4xl hover:text-[#EB1616] hover:bg-[#000000] text-[#6C7293] w-[88%] px-7 text-[17px] ">
         
         <i className="fa-solid fa-clock-rotate-left me-2 bg-[#000000] p-3 rounded-[50%] "></i>
          <span>History</span>
        </a>
        <a href="/" className="flex items-center transition capitalize py-2 rounded-tr-4xl rounded-br-4xl hover:text-[#EB1616] hover:bg-[#000000] text-[#6C7293] w-[88%] px-7 text-[17px] ">
          <i className="fa-solid fa-right-to-bracket me-2 bg-[#000000] p-3 rounded-[50%] "></i>
          <span>Login</span>
        </a>
        <a href="/" className="flex items-center transition capitalize py-2 rounded-tr-4xl rounded-br-4xl hover:text-[#EB1616] hover:bg-[#000000] text-[#6C7293] w-[88%] px-7 text-[17px] ">
          <i className="fa-solid fa-registered me-2 bg-[#000000] p-3 rounded-[50%] "></i>
          <span>Register</span>
        </a>
        <a href="/" className="flex items-center transition capitalize py-2 rounded-tr-4xl rounded-br-4xl hover:text-[#EB1616] hover:bg-[#000000] text-[#6C7293] w-[88%] px-7 text-[17px] ">
          <i className="fa-solid fa-dungeon me-2 bg-[#000000] p-3 rounded-[50%] "></i>
          <span>Premium</span>
        </a>
        <a href="/" className="flex items-center transition capitalize py-2 rounded-tr-4xl rounded-br-4xl hover:text-[#EB1616] hover:bg-[#000000] text-[#6C7293] w-[88%] px-7 text-[17px] ">
          <i className="fa-brands fa-hire-a-helper me-2 bg-[#000000] p-3 rounded-[50%] "></i>
          <span>Support</span>
        </a>
      </div>
    </motion.div>
  );
};

export default Sidebar;
