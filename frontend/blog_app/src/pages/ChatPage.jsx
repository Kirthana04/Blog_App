import React from 'react';
import StreamingChatbotComponent from '@/components/StreamingChatbot';
import Sidebar from '@/components/sidebar';

const ChatPage = () => {
  return (
    <div className={`flex h-screen bg-gray-100`}>
      <Sidebar />
      <div className="flex-1 overflow-y-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className={`text-3xl font-bold text-gray-500`}>BloQ.</h1>
        </div>
        <div className="max-w-4xl mx-auto">
          <StreamingChatbotComponent />
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
