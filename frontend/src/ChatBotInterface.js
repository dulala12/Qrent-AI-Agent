import { useState, useEffect, useRef } from 'react';
import questionFlow from './utils/questionFlow';
import chatbotUtils from './utils/chatbotUtils';
import Sidebar from './components/Sidebar';
import Message from './components/Message';
import TypingIndicator from './components/TypingIndicator';
import ChatInput from './components/ChatInput';
import './chatBot.css';

export default function ChatbotInterface({ onSubmit }) {
    const [conversations] = useState([
        { id: 1, title: '租房需求咨询 - 2024/11/01', active: true },
      ]);

  const { generateSummary, getInputPlaceholder, getInitialMessages } = chatbotUtils;
  const [messages, setMessages] = useState(getInitialMessages());
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState('university');
  const [formData, setFormData] = useState({});
  const messagesEndRef = useRef(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addBotMessage = (content, options = null, question = null) => {
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      const newMessage = {
        id: Date.now(),
        type: 'bot',
        content,
        options,
        question,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, newMessage]);
    }, 800);
  };

  const addUserMessage = (content) => {
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
  };

  const proceedToNextQuestion = (currentQ, nextQ) => {
    if (nextQ && nextQ !== 'complete') {
      setTimeout(() => {
        const questionData = questionFlow[nextQ];
        addBotMessage(questionData.botMessage, questionData.options || null, nextQ);
        setCurrentQuestion(nextQ);
      }, 1000);
    }else if (nextQ === 'complete' && currentQ !== 'flexibility') {
        showSummary();
    }
  };

  const handleOptionClick = (option) => {
    addUserMessage(option);
    setFormData((prev) => ({ ...prev, [currentQuestion]: option }));

    if (currentQuestion === 'university') {
      const nextQ = questionFlow['university'].next;
      proceedToNextQuestion(currentQuestion, nextQ);
      return;
    }
    
    if (currentQuestion === 'roomType' && (option === 'Studio' || option === '一居室')) {
      setTimeout(() => {
        addBotMessage(
          '如果选择 Studio 或一居室，是否考虑合租以降低成本？',
          ['愿意', '不愿意', '视情况而定'],
          'sharedRoom'
        );
        setCurrentQuestion('sharedRoom');
      }, 1000);
      return;
    }

    if (currentQuestion === 'sharedRoom') {
      const nextQ = questionFlow['roomType'].next;
      proceedToNextQuestion(currentQuestion, nextQ);
      return;
    }

    if (currentQuestion === 'leaseTerm' && option === '其他') {
      setTimeout(() => {
        addBotMessage('请告诉我您期望的租期是多久？', null, 'leaseTermOther');
        setCurrentQuestion('leaseTermOther');
      }, 1000);
      return;
    }

    const nextQuestion = questionFlow[currentQuestion]?.next;
    proceedToNextQuestion(currentQuestion, nextQuestion);
  };

  const handleBudgetConfirm = (minBudget, maxBudget) => {
    addUserMessage(`最低预算：${minBudget} 澳元/周，最高预算：${maxBudget} 澳元/周`);
    setFormData((prev) => ({ ...prev, minBudget, maxBudget }));

    const nextQuestionKey = questionFlow.budget.next;
    const nextQuestion = questionFlow[nextQuestionKey];

    setTimeout(() => {
      addBotMessage(nextQuestion.botMessage, nextQuestion.options, nextQuestionKey);
      setCurrentQuestion(nextQuestionKey);
    }, 1000);
  };

  const handleMultiSelectConfirm = (selectedOptions) => {
    addUserMessage(
      selectedOptions.length > 0 ? selectedOptions.join('、') : '未选择任何选项'
    );
    setFormData((prev) => ({ ...prev, flexibility: selectedOptions }));
    showSummary();
  };

  const showSummary = () => {
    setTimeout(() => {
        addBotMessage('好的，我来帮您总结一下您的租房需求：');
      setTimeout(() => {
        const summary = generateSummary(formData);
        addBotMessage(summary);
        if (onSubmit) onSubmit(formData);
      }, 1500);
    }, 800);
  };

  const handleSend = () => {
    if (!inputValue.trim()) return;
    addUserMessage(inputValue);
    setFormData((prev) => ({ ...prev, [currentQuestion]: inputValue }));

    const nextQuestion = questionFlow[currentQuestion]?.next;
    if (nextQuestion && nextQuestion !== 'complete') {
      proceedToNextQuestion(currentQuestion, nextQuestion);
    }
    setInputValue('');
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentQuestion('university');
    setFormData({});
    setInputValue('');
    const firstQ = questionFlow['university'];
    addBotMessage(firstQ.botMessage, firstQ.options, 'university');
  };

  return (
    <div className="chatbot-container">
      <Sidebar conversations={conversations} onNewChat={handleNewChat} />

      <div className="chat-main">
        <div className="chat-header"></div>
        <div className="messages-container">
          <div className="messages-wrapper">
            {messages.map((message) => (
              <Message
                key={message.id}
                message={message}
                questionFlow={questionFlow}
                onOptionClick={handleOptionClick}
                onBudgetConfirm={handleBudgetConfirm}
                onMultiSelectConfirm={handleMultiSelectConfirm}
              />
            ))}
            {isTyping && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <ChatInput
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSend}
          placeholder={getInputPlaceholder(currentQuestion)}
        />
      </div>
    </div>
  );
}
