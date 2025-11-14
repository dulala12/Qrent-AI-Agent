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
                请输入入住日期 (格式: yyyy/mm/dd)：
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  placeholder="yyyy/mm/dd"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
                  // 只允许输入数字和斜杠
                  onInput={(e) => {
                    e.target.value = e.target.value.replace(/[^\d/]/g, '');
                  }}
                  ref={(input) => {
                    if (input) {
                      // 添加输入格式化逻辑
                      input.addEventListener('input', function(e) {
                        let value = e.target.value;
                        // 移除所有非数字字符
                        let numbers = value.replace(/[^\d]/g, '');
                        // 格式化日期
                        let formatted = '';
                        if (numbers.length > 0) {
                          formatted = numbers.slice(0, 4);
                          if (numbers.length > 4) {
                            formatted += '/' + numbers.slice(4, 6);
                            if (numbers.length > 6) {
                              formatted += '/' + numbers.slice(6, 8);
                            }
                          }
                        }
                        e.target.value = formatted;
                      });
                    }
                  }}
                  id={`date-input-${message.id}`}
                />
                <button
                  onClick={() => {
                    const dateInput = document.getElementById(`date-input-${message.id}`);
                    if (dateInput && dateInput.value) {
                      // 验证日期格式
                      const dateRegex = /^\d{4}\/\d{2}\/\d{2}$/;
                      if (dateRegex.test(dateInput.value)) {
                        onOptionClick(dateInput.value);
                      } else {
                        alert('请输入正确的日期格式：yyyy/mm/dd');
                      }
                    } else {
                      alert('请输入入住日期');
                    }
                  }}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm whitespace-nowrap"
                >
                  确认日期
                </button>
              </div>
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
