import { Send } from 'lucide-react';
import '../chatBot.css';

const ChatInput = ({ value, onChange, onSend, placeholder }) => {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      onSend();
    }
  };

  return (
    <div className="chat-input-container">
      <div className="chat-input-wrapper">
        <div className="input-box">
          <input
            type="text"
            placeholder={placeholder || '输入您的回答...'}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyPress={handleKeyPress}
            className="chat-input"
          />
          <button onClick={onSend} className="send-btn">
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
