import BudgetInputPanel from './BudgetInputPanel';
import OptionsPanel from './OptionsPanel';
import { Sparkles } from 'lucide-react';
import '../chatBot.css';

const Message = ({ message, questionFlow, onOptionClick, onBudgetConfirm, onMultiSelectConfirm }) => {
  // ✅ 判断当前问题是否为“输入型问题”（即预算问卷）
  const isInputQuestion = message.options?.some(opt => opt.type === 'input');

  if (message.type === 'user') {
    return (
      <div className="message user">
        <div className="message-content">
          <div className="message-bubble user-bubble">
            <p className="message-text">{message.content}</p>
          </div>
        </div>
        <div className="message-avatar user-avatar-msg">用</div>
      </div>
    );
  }

  return (
    <div className="message bot">
      <div className="message-avatar bot-avatar">
        <Sparkles size={20} />
      </div>

      <div className="message-content">
        <div className="message-bubble bot-bubble">
          <p className="message-text">{message.content}</p>

          
          {isInputQuestion && (
            <BudgetInputPanel onConfirm={onBudgetConfirm} />
          )}

          
          {message.question === 'moveInDate' && (
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-600 mb-2">
                请选择入住日期：
              </label>
              <input
                type="date"
                onChange={(e) => onOptionClick(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
              />
            </div>
          )}

          
          {!isInputQuestion && message.options && message.question !== 'moveInDate' && (
            <OptionsPanel
              options={message.options}
              question={message.question}
              multiSelect={questionFlow[message.question]?.multiSelect}
              onOptionClick={onOptionClick}
              onMultiSelectConfirm={onMultiSelectConfirm}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Message;
