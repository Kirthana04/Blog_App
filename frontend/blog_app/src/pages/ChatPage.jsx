import React from 'react';
import ChatbotComponent from '@/components/Chatbot';
import Sidebar from '@/components/sidebar';
import { useSelector } from "react-redux";


const ChatPage = () => {
  return (
    <div className={`flex h-screen bg-gray-100`}>
      <Sidebar />
      <div className="flex-1 overflow-y-auto p-6">
        <h1 className={`text-3xl font-bold mb-6 text-gray-500`}>BloQ.</h1>
        <div className="max-w-4xl mx-auto">
          <ChatbotComponent />
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
