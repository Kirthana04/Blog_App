import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Sidebar from "@/components/sidebar";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";

export default function BlogDetail() {
  const { id } = useParams();
  const [blog, setBlog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`http://localhost:8000/blogs/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch blog");
        return res.json();
      })
      .then((data) => setBlog(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="flex items-center justify-center h-screen">Loading blog...</div>;
  if (error) return <div className="flex items-center justify-center h-screen text-red-500">Error: {error}</div>;
  if (!blog) return <div className="flex items-center justify-center h-screen">Blog not found.</div>;

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 overflow-y-auto p-6 max-w-3xl mx-auto mt-10 w-full" style={{width: '100%', maxWidth: '1000px'}}>
        <Card className="shadow-lg bg-gray-100 w-full">
          <CardHeader>
            <CardTitle className="text-3xl font-bold text-center text-gray-700">{blog.title}</CardTitle>
            <CardDescription className="text-gray-700 text-center">{blog.description}</CardDescription>
          </CardHeader>
          <CardContent className="text-gray-700 justify-center text-lg">
            {blog.image && (
              <img
                src={`http://localhost:8000${blog.image}`}
                alt={blog.title}
                className="w-full object-cover rounded-lg mb-6 h-auto"
              />
            )}
            <p className="whitespace-pre-wrap">{blog.contents}</p>
          </CardContent>
          <CardFooter>
            <div className="flex flex-wrap gap-2 mt-2">
                      {blog.tags?.map((tag, index) => (
                        <span
                          key={index}
                          className=" bg-gray-500 text-gray-50 text-xs px-2 py-1 rounded-full"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
          </CardFooter>
        </Card>
        <Link to="/blogfeed" className="inline-block mt-6 text-gray-600 hover:underline">
          ← Back to Blog Feed
        </Link>
      </div>
    </div>
  );
}
