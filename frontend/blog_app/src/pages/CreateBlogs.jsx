import React, { useState } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import Sidebar from "@/components/sidebar";

export default function CreateBlog() {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    contents: "",
    imageBase64: "",
    tags: "",
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Handle text input changes
  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  // Handle image upload
  function handleImageChange(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      const base64String = reader.result.split(",")[1];
      setFormData((prev) => ({ ...prev, imageBase64: base64String }));
    };
    reader.readAsDataURL(file);
  }

  // Validate form fields
  function validateForm() {
    let newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = "Title is required";
    } else if (formData.title.length < 3) {
      newErrors.title = "Title must be at least 3 characters long";
    }

    if (!formData.description.trim()) {
      newErrors.description = "Description is required";
    } else if (formData.description.length > 400) {
      newErrors.description = "Description must be under 200 characters";
    }

    if (!formData.contents.trim()) {
      newErrors.contents = "Content is required";
    }

    if (formData.tags) {
      const tagList = formData.tags
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean);

      if (tagList.length > 8) {
        newErrors.tags = "You can only add up to 5 tags";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);

    const payload = {
      title: formData.title,
      description: formData.description,
      contents: formData.contents,
      image: formData.imageBase64 || null,
      tags: formData.tags
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
    };

    const token = localStorage.getItem("access_token");

    try {
      const res = await fetch("http://localhost:8000/blogs/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.message || "Failed to create blog");
      }

      alert("Blog created successfully!");
      navigate("/blogfeed");

      setFormData({
        title: "",
        description: "",
        contents: "",
        imageBase64: "",
        tags: "",
      });
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 overflow-y-auto p-6 max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-10 text-gray-500">
          Create New Blog .
        </h1>
        <form
          onSubmit={handleSubmit}
          className="max-w-3xl mx-auto p-6 space-y-6 bg-gray-100 rounded-md shadow"
        >
          {/* Title */}
          <div>
            <Label htmlFor="title" className="mb-2">
              Title
            </Label>
            <Input
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="Enter blog title"
              className={`border p-2 rounded-md w-full ${
                errors.title ? "border-black" : "border-gray-300"
              }`}
            />
            {errors.title && (
              <p className="text-black text-sm mt-1">{errors.title}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <Label htmlFor="description" className="mb-2">
              Description
            </Label>
            <Textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Short description"
              rows={3}
              className={`border p-2 rounded-md w-full ${
                errors.description ? "border-black" : "border-gray-300"
              }`}
            />
            {errors.description && (
              <p className="text-black text-sm mt-1">{errors.description}</p>
            )}
          </div>

          {/* Contents */}
          <div>
            <Label htmlFor="contents" className="mb-2">
              Content
            </Label>
            <Textarea
              id="contents"
              name="contents"
              value={formData.contents}
              onChange={handleChange}
              placeholder="Full blog content"
              rows={6}
              className={`border p-2 rounded-md w-full ${
                errors.contents ? "border-black" : "border-gray-300"
              }`}
            />
            {errors.contents && (
              <p className="text-black text-sm mt-1">{errors.contents}</p>
            )}
          </div>

          {/* Image Upload */}
          <div>
            <Label htmlFor="image" className="mb-2">
              Upload Image
            </Label>
            <Input
              id="image"
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="border border-gray-300 p-2 rounded-md w-full"
            />
          </div>

          {/* Tags */}
          <div>
            <Label htmlFor="tags" className="mb-2">
              Tags (comma separated)
            </Label>
            <Input
              id="tags"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              placeholder="example: tech, programming, AI"
              className={`border p-2 rounded-md w-full ${
                errors.tags ? "border-black" : "border-gray-300"
              }`}
            />
            {errors.tags && (
              <p className="text-black text-sm mt-1">{errors.tags}</p>
            )}
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={loading}
            className="bg-gray-500 hover:bg-gray-700 text-white"
          >
            {loading ? "Creating..." : "Create Blog"}
          </Button>
        </form>
      </div>
    </div>
  );
}
