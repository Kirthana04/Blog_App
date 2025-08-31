import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import BlogFeed from "./pages/BlogFeed";
import BlogDetail from "./pages/BlogDetail";
import OwnBlogs from "./pages/OwnBlog";
import CreateBlog from "./pages/CreateBlogs";
import ChatPage from "./pages/ChatPage";


export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/blogfeed" element={<BlogFeed />} />
        <Route path="/blogs/:id" element={<BlogDetail />} />
        <Route path="/ownblog" element={<OwnBlogs />} />
        <Route path="/createblogs" element={<CreateBlog />} />
        <Route path="/chat" element={<ChatPage />} />
      </Routes>
    </Router>
  );
}
