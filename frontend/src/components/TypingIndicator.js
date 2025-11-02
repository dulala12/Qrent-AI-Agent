import { Sparkles } from 'lucide-react';
import '../chatBot.css';

const TypingIndicator = () => {
  return (
    <div className="typing-indicator">
      <div className="message-avatar bot-avatar">
        <Sparkles size={20} />
      </div>
      <div className="typing-bubble">
        <div className="typing-dots">
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
