import Sidebar from "@/components/sidebar";
import React, { useEffect, useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export default function OwnBlogs() {
  const [blogs, setBlogs] = useState([]);
  const [loading, setLoading] = useState(true);
  // Remove error state

  // Assuming token is stored in localStorage
  const token = localStorage.getItem("access_token");
  console.log("Token:", token);

  // Fetch user's blogs
  useEffect(() => {
    setLoading(true);
    fetch("http://localhost:8000/blogs/my", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) {
          // Auto-logout and redirect on error
          localStorage.removeItem("access_token");
          window.location.href = "/";
          alert("Session expired! Please log in again.");
          return;
        }
        return res.json();
      })
      .then((data) => {
        if (data) setBlogs(data);
      })
      .finally(() => setLoading(false));
  }, [token]);

  // Delete handler - calls soft delete API
  async function handleDelete(blogId) {
    if (!window.confirm("Are you sure you want to delete this blog?")) return;

    try {
      const res = await fetch(`http://localhost:8000/blogs/delete/${blogId}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.message || "Failed to delete blog");
      }

      // Update UI - remove deleted blog from list
      setBlogs((prev) => prev.filter((b) => b.id !== blogId));
    } catch (err) {
      alert(err.message);
    }
  }

  if (loading) return <div>Loading your blogs...</div>;
  if (blogs.length === 0) return <div>You have no blogs yet.</div>;

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 overflow-y-auto p-6">
        <div>
          <h1 className="text-3xl font-bold mb-3 p-6 text-gray-500">
            My Blogs .
          </h1>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 ">
            {blogs.map((blog) => (
              <Link key={blog.id} to={`/blogs/${blog.id}`}>
                <Card
                  key={blog.id}
                  className="shadow-lg hover:shadow-xl transition-shadow duration-200 cursor-pointer bg-gray-200"
                >
                  <CardHeader>
                    <CardTitle  className="text-center text-gray-700 font-bold text-lg ">{blog.title}</CardTitle>
                  </CardHeader>

                <CardContent>
                  <p className="text-center text-gray-700 -mt-4">{blog.description}</p>

                  {blog.image && (
                    <img
                      src={`http://localhost:8000${blog.image}`}
                      alt={blog.title}
                      className=" mt-4 mb-4 rounded"
                      style={{ maxWidth: "100%" }}
                    />
                  )}

                  {blog.tags && blog.tags.length > 0 && (
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
                  )}
                </CardContent>

                <CardFooter>
                  <Button
                    className="bg-gray-500 hover:bg-gray-600 text-white"
                    variant="destructive"
                    onClick={() => handleDelete(blog.id)}
                  >
                    Delete
                  </Button>
                </CardFooter>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </div>
    </div>
  );
}
