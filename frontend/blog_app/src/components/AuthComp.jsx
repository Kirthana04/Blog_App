import React, { useState, useEffect } from "react";
import { Mail, Lock, Eye, EyeOff, User } from "react-feather";
import { useNavigate } from "react-router-dom";


export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    username: "",
  });

  const [loggedInUser, setLoggedInUser] = useState(null);
  const [protectedData, setProtectedData] = useState(null);
  const navigate = useNavigate();

  // On mount, check if token and username exist in localStorage
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const username = localStorage.getItem("username");
    if (token && username) {
      setLoggedInUser({ username });
    }
  }, []);

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    console.log("isLoginvalue:", isLogin);
    e.preventDefault();

    const url = isLogin
      ? "http://127.0.0.1:8000/login"
      : "http://127.0.0.1:8000/signup";

    const payload = isLogin
      ? { email: formData.email, password: formData.password }
      : {
          username: formData.username,
          email: formData.email,
          password: formData.password,
        };

    console.log("Submitting form to:", url);
    console.log("Payload:", payload);

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(JSON.stringify(data) || "Something went wrong"); // editted
      }

      if (isLogin) {
        // Save JWT token & username
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("username", data.user.username);
        setLoggedInUser({ username: data.user.username });
        navigate("/blogfeed");
      } else {
        alert(data.message || "Account created successfully!");
        setIsLogin(true); // Switch to login form
      }

      setFormData({ email: "", password: "", username: "" }); // Clear form
    } catch (err) {
      console.error("Error:", err);
      alert(err.message);
    }
  }

  async function fetchProtectedData() {
    const token = localStorage.getItem("access_token");
    if (!token) {
      alert("No token found, please login first.");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/protected", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        throw new Error("Failed to fetch protected data");
      }

      const result = await res.json();
      setProtectedData(result.message);
    } catch (error) {
      alert(error.message);
    }
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    setLoggedInUser(null);
    setProtectedData(null);
    setFormData({ email: "", password: "", username: "" });
    setIsLogin(true);
  }

 

  return (
    // Root: remove h-screen/grid so it fits nicely in modal, make card shape
    <div className="flex justify-center items-center w-full border-gray-300">
      <div className="w-full max-w-sm sm:max-w-md rounded-xl shadow-xl border border-base-300 bg-base-200 p-2 sm:p-8">
        <div className="space-y-8">
          {/* Title */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold mt-2">
              {isLogin ? "Welcome Back" : "Create Account"}
            </h1>
            <p className="text-base-content/60">
              {isLogin
                ? "Sign in to your account"
                : "Fill the form to create a new account"}
            </p>
          </div>

          {/* Form */}
          <form className="space-y-6" onSubmit={handleSubmit}>
            {!isLogin && (
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-medium">Username</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-base-content/40" />
                  </div>
                  <input
                    type="text"
                    name="username"
                    className="input input-bordered w-full pl-10"
                    placeholder="Username"
                    value={formData.username}
                    onChange={handleChange}
                    required={!isLogin}
                  />
                </div>
              </div>
            )}

            {/* Email */}
            <div className="form-control">
              <label className="label">
                <span className="label-text font-medium">Email</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-base-content/40" />
                </div>
                <input
                  type="email"
                  name="email"
                  className="input input-bordered w-full pl-10"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div className="form-control">
              <label className="label">
                <span className="label-text font-medium">Password</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-base-content/40" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  className="input input-bordered w-full pl-10"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword((prev) => !prev)}
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-base-content/40" />
                  ) : (
                    <Eye className="h-5 w-5 text-base-content/40" />
                  )}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button type="submit" className="btn btn-primary w-full">
              {isLogin ? "Sign in" : "Sign up"}
            </button>
          </form>

          {/* Switch Between Login/Signup */}
          <div className="text-center pt-2">
            {isLogin ? (
              <p className="text-base-content/60">
                Don&apos;t have an account?{" "}
                <button
                  type="button"
                  className="link link-primary"
                  onClick={() => setIsLogin(false)}
                >
                  Create account
                </button>
              </p>
            ) : (
              <p className="text-base-content/60">
                Already have an account?{" "}
                <button
                  type="button"
                  className="link link-primary"
                  onClick={() => setIsLogin(true)}
                >
                  Sign in
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
