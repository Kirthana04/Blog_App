import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthComp from "../components/AuthComp";


export default function HomePage() {
  const [showLogin, setShowLogin] = useState(false);
  const [blogs, setBlogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate(); // <-- add this

  // Fetch blogs from backend
  // Navigate to login page when Login button is clicked
  const handleLoginClick = () => {
    navigate("/login");
  };

  // On blog click open the login popup instead of alert
  const handleBlogClick = () => {
    setShowLogin(true);
  };

  useEffect(() => {
    async function fetchBlogs() {
      setLoading(true);
      try {
        const response = await fetch("http://localhost:8000/blogs/");
        if (!response.ok) throw new Error("Failed to fetch blogs");
        const data = await response.json();
        // Slice to limit to 12 blogs
        const limitedBlogs = data.slice(0, 12);
        setBlogs(limitedBlogs);
      } catch (err) {
        console.error(err);
        setBlogs([]);
      } finally {
        setLoading(false);
      }
    }
    fetchBlogs();
  }, []);

  return (
    <div>
      {/* Header */}
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          padding: "1rem 2rem",
          backgroundColor: "#9CA3AF",
          color: "white",
          alignItems: "center",
          position: "relative"
        }}
      >
        <img
          src="logo.svg"
          alt="Placeholder"
          style={{
            display: "block",
            width: "500%",
            maxWidth: "150px",
            margin: "1rem 0 1rem 0"
          }}
        />
        <h2 className="mr-120"
          style={{
            fontFamily: "'Pinyon Script', cursive",
            textAlign: "center",
            fontSize: "7rem",
            fontWeight: "normal"
          }}
        >
          BlogStudio.
        </h2>
        {/* Login SVG on right side */}
        <div
          style={{
            position: "absolute",
            top: "1.5rem",
            right: "2rem",
            cursor: "pointer",
            zIndex: 10
          }}
          onClick={() => setShowLogin(true)}
        >
          <img src="/Login.svg" alt="Login" style={{ width: "150px", height: "150px" }} />
        </div>
      </header>

      {showLogin && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            justifyContent: "center",
            alignItems: "flex-start",
            paddingTop: "10vh", // push popup a bit lower from very top
            zIndex: 9999,
          }}
          onClick={() => setShowLogin(false)}
        >
          <div
            style={{
              position: "relative",
              backgroundColor: "white",
              padding: "2.25rem 2rem 2rem",
              borderRadius: "14px",
              maxWidth: "420px",
              width: "100%",
              boxShadow: "0 8px 28px rgba(0,0,0,0.28)"
            }}
            onClick={e => e.stopPropagation()}
          >
            <AuthComp />
          </div>
        </div>
      )}

      {/* Main content */}
      <main
        style={{
          padding: "2rem",
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "1.5rem",
        }}
      >
        {loading ? (
          <p>Loading blogs...</p>
        ) : blogs.length === 0 ? (
          <p>No blogs found.</p>
        ) : (
          blogs.map((blog) => (
            <div
              key={blog.id}
              onClick={handleBlogClick}
              style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "1rem",
                cursor: "pointer",
              }}
            >
              <img
                src={`http://localhost:8000${blog.image}`}
                alt={blog.title}
                style={{ width: "100%", borderRadius: "6px" }}
              />
              <h3 className="text-lg font-semibold text-gray-700 text-center" style={{ marginTop: "0.5rem" }}>{blog.title}</h3>
              <p className="text-gray-600 text-center">{blog.description}</p>
            </div>
          ))
        )}
      </main>
    </div>
  );
}
