import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { toggleTheme } from "@/store/themeslicer";

export default function Sidebar() {
  const theme = useSelector((state) => state.theme.theme);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/");
  }

  // Sidebar bg changes based on theme
  const sidebarBg = theme === "dark" ? "bg-black text-white" : "bg-gray-400 text-white";

  return (
    <div className={`w-64 h-screen p-5 flex flex-col ${sidebarBg}`}>
      <img src="/logo.svg" alt="Logo" className="h-10 w-10 mb-4" />
      <h2 className="text-2xl font-extrabold mb-10 -mt-13 ml-14">BlogStudio.</h2>

      {/* Toggle switch below BlogStudio */}
      <label className="switch mb-6">
        <input
          type="checkbox"
          checked={theme === "dark"}
          onChange={() => dispatch(toggleTheme())}
        />
        <span className="slider round"></span>
      </label>

      <nav className="flex flex-col gap-4 flex-grow">
        <Link to="/blogfeed" className="hover:bg-gray-500 p-2 rounded">
          Blogs Feed
        </Link>
        <Link to="/ownblog" className="hover:bg-gray-500 p-2 rounded">
          My Blogs
        </Link>
        <Link to="/createblogs" className="hover:bg-gray-500 p-2 rounded">
          Create Blogs
        </Link>
        <button
          onClick={handleLogout}
          className="px-2 py-2 text-white rounded text-left hover:bg-gray-500"
        >
          Logout
        </button>
      </nav>

  <style>{`
        .switch {
          position: relative;
          display: inline-block;
          width: 50px;
          height: 24px;
        }

        .switch input {
          opacity: 0;
          width: 0;
          height: 0;
        }

        .slider {
          position: absolute;
          cursor: pointer;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: #ccc;
          transition: 0.4s;
          border-radius: 24px;
        }

        .slider:before {
          position: absolute;
          content: "";
          height: 18px;
          width: 18px;
          left: 3px;
          bottom: 3px;
          background-color: white;
          transition: 0.4s;
          border-radius: 50%;
        }

        input:checked + .slider {
          background-color: #2196f3;
        }

        input:checked + .slider:before {
          transform: translateX(26px);
        }
      `}</style>
    </div>
  );
}
