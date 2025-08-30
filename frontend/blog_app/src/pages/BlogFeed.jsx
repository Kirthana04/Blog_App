import React, { useState, useEffect } from "react";
import AuthComp from "@/components/AuthComp";
import Sidebar from "@/components/sidebar";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Link } from "react-router-dom";

export default function BlogFeed() {
  const [blogs, setBlogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showAuth, setShowAuth] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/blogs/", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    })
      .then((res) => {
        if (res.status === 401) {
          alert("Session expired. Please login again.");
          localStorage.removeItem("access_token");
          window.location.href = "/";
          return null;
        }
        if (!res.ok) {
          throw new Error("Failed to fetch blogs");
        }
        return res.json();
      })
      .then((data) => {
        if (data) {
          setBlogs(data);
        }
        setLoading(false);
      })
      .catch(() => {
        localStorage.removeItem("access_token");
        window.location.href = "/";
      });
  }, []);

  if (loading)
    return (
      <div className="flex items-center justify-center h-screen">
        Loading blogs...
      </div>
    );

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 overflow-y-auto p-6 relative">
        <h1 className="text-3xl font-bold mb-6 text-gray-500">Blog Feed .</h1>

        {/* Search Bar */}
        <div className="mb-6 -mt-14 flex justify-end border-gray-500">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by tag or title..."
            className="w-full max-w-md px-4 py-2 border border-gray-400 bg-gray-100 rounded shadow-lg focus:outline-none focus:border-gray-600"
          />
        </div>

        {/* Auth Modal */}
        {showAuth && (
          <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl p-4 relative">
              <button
                className="absolute top-2 right-2 text-gray-500 hover:text-gray-700 text-xl font-bold"
                onClick={() => setShowAuth(false)}
                aria-label="Close"
              >
                &times;
              </button>
              <AuthComp />
            </div>
          </div>
        )}

        {blogs.length === 0 ? (
          <p>No blogs available.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 ">
            {blogs
              .filter((blog) => {
                const q = search.trim().toLowerCase();
                if (!q) return true;
                const titleMatch = blog.title?.toLowerCase().includes(q);
                const tagMatch = blog.tags?.some((tag) =>
                  tag.toLowerCase().includes(q)
                );
                return titleMatch || tagMatch;
              })
              .map((blog) => (
                <Link
                  key={blog.id}
                  to={`/blogs/${blog.id}`}
                  className="block hover:no-underline"
                >
                  <Card className="shadow-lg hover:shadow-xl transition-shadow duration-200 cursor-pointer bg-gray-200">
                    <CardHeader>
                      <CardTitle className="text-center text-gray-700 font-bold text-lg ">
                        {blog.title}
                      </CardTitle>
                      <CardDescription className="text-center text-gray-700">
                        {blog.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {blog.image && (
                        <img
                          src={`http://localhost:8000${blog.image}`}
                          alt={blog.title}
                          className="w-full h-48 object-cover rounded-lg mb-4 border-2 border-gray-400"
                        />
                      )}
                    </CardContent>
                    <CardFooter>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {blog.tags?.map((tag, index) => (
                          <span
                            key={index}
                            className="bg-gray-500 text-gray-100 text-xs font-semibold px-2 py-1 rounded-full"
                          >
                            #{tag}
                          </span>
                        ))}
                      </div>
                    </CardFooter>
                  </Card>
                </Link>
              ))}
          </div>
        )}
      </div>
    </div>
  );
}
