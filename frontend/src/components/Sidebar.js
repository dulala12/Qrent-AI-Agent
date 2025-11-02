import React from 'react';
import { Plus, MessageSquare  } from 'lucide-react';
import '../chatBot.css';

const Sidebar = ({ conversations, onNewChat }) => {
  return (
    <div className="chatbot-sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">租房助手 AI</h1>
        <button className="new-chat-btn" onClick={onNewChat}>
          <Plus size={18} />
          <span>新的咨询</span>
        </button>
      </div>

      <div className="conversations-section">
        <div className="conversations-header">
          <span>历史对话</span>
        </div>

        <div className="conversation-list">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              className={`conversation-item ${conv.active ? 'active' : ''}`}
            >
              <MessageSquare size={18} />
              <span>{conv.title}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
