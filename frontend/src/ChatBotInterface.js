import { useState, useEffect, useRef } from 'react';
import questionFlow from './utils/questionFlow';
import chatbotUtils from './utils/chatbotUtils';
import Sidebar from './components/Sidebar';
import Message from './components/Message';
import TypingIndicator from './components/TypingIndicator';
import ChatInput from './components/ChatInput';
import './chatBot.css';

export default function ChatbotInterface({ onSubmit, analysisResult }) {
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
  const analysisResultRef = useRef(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addBotMessage = (content, options = null, question = null, customId = null) => {
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      const newMessage = {
        id: customId || Date.now(),
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

    // 防止重复处理问题的标记
    let shouldProceedToNext = true;

    // 特殊问题处理
    if (currentQuestion === 'university') {
      const nextQ = questionFlow['university'].next;
      proceedToNextQuestion(currentQuestion, nextQ);
      shouldProceedToNext = false;
    }
    
    else if (currentQuestion === 'roomType' && (option === 'Studio' || option === '一居室')) {
      setTimeout(() => {
        addBotMessage(
          '如果选择 Studio 或一居室，是否考虑合租以降低成本？',
          ['愿意', '不愿意', '视情况而定'],
          'sharedRoom'
        );
        setCurrentQuestion('sharedRoom');
      }, 1000);
      shouldProceedToNext = false;
    }

    else if (currentQuestion === 'sharedRoom') {
      const nextQ = questionFlow['roomType'].next;
      proceedToNextQuestion(currentQuestion, nextQ);
      shouldProceedToNext = false;
    }

    else if (currentQuestion === 'leaseTerm' && option === '其他') {
      setTimeout(() => {
        addBotMessage('请告诉我您期望的租期是多久？', null, 'leaseTermOther');
        setCurrentQuestion('leaseTermOther');
      }, 1000);
      shouldProceedToNext = false;
    }

    // 处理特殊的leaseTermOther问题
    else if (currentQuestion === 'leaseTermOther') {
      const nextQ = questionFlow['leaseTerm'].next;
      proceedToNextQuestion(currentQuestion, nextQ);
      shouldProceedToNext = false;
    }

    // 标准问题流程
    if (shouldProceedToNext) {
      const nextQuestion = questionFlow[currentQuestion]?.next;
      // 确保nextQuestion存在且不是'complete'才继续
      if (nextQuestion && nextQuestion !== 'complete') {
        proceedToNextQuestion(currentQuestion, nextQuestion);
      } else if (nextQuestion === 'complete') {
        // 直接显示总结
        setTimeout(() => {
          showSummary();
        }, 1000);
      }
    }
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
        
        // 添加进度显示消息
        const progressMessageId = Date.now();
        addBotMessage('AI分析正在进行中...', null, null, progressMessageId);
        
        // 发送请求并跟踪进度
        if (onSubmit) {
          // 提交数据并获取analysisId
          onSubmit(formData)
            .then(analysisId => {
              // 定期查询进度
              const progressInterval = setInterval(() => {
                // 查询进度的API调用
                fetch(`/survey/progress/${analysisId}/`)
                  .then(response => response.json())
                  .then(data => {
                    if (data && data.stage) {
                      // 更新进度消息 - 使用content属性
                      updateProgressMessage(progressMessageId, `AI分析正在进行中...\n当前阶段：${data.stage}\n进度：${data.percentage || 0}%`);
                      
                      // 检查是否完成
                      if (data.completed) {
                        clearInterval(progressInterval);
                        // 获取最终结果
                        fetch(`/survey/result/${analysisId}/`)
                          .then(response => response.json())
                          .then(result => {
                            if (result && result.ok) {
                              // 使用content属性传递消息内容
                              addBotMessage(`AI分析完成：\n${result.summary || '分析完成，请查看右侧报告。'}`);
                            } else {
                              // 使用content属性传递消息内容
                              addBotMessage(`AI分析失败：${result.error || '未知错误'}`);
                            }
                          })
                          .catch(error => {
                            // 使用content属性传递消息内容
                            addBotMessage(`获取分析结果失败：${error.message}`);
                            clearInterval(progressInterval);
                          });
                      }
                    }
                  })
                  .catch(error => {
                    console.error('获取进度失败:', error);
                    // 只在发生严重错误时停止轮询
                    if (error.message.includes('Network')) {
                      clearInterval(progressInterval);
                      // 使用content属性传递消息内容
                      addBotMessage('网络错误：无法获取分析进度，请稍后重试。');
                    }
                  });
              }, 2000); // 每2秒查询一次进度
              
              // 防止无限轮询的安全措施（最多查询30分钟）
              setTimeout(() => {
                clearInterval(progressInterval);
                // 如果分析仍在进行中，提供手动查询选项
                addBotMessage('分析时间较长，您可以稍后再次发起查询。');
              }, 1800000);
            })
            .catch(error => {
              console.error('提交失败:', error);
              // 使用content属性更新消息内容
              updateProgressMessage(progressMessageId, `提交失败：${error.message}\n请稍后重试。`);
            });
        }
      }, 1500);
    }, 800);
  };
  
  // 更新进度消息的辅助函数
  const updateProgressMessage = (messageId, newContent) => {
    setMessages(prevMessages => 
      prevMessages.map(msg => 
        msg.id === messageId ? { ...msg, content: newContent } : msg
      )
    );
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

  useEffect(() => {
    if (!analysisResult) return;
    if (analysisResultRef.current === analysisResult) return;
    analysisResultRef.current = analysisResult;

    if (analysisResult.ok) {
      const summaryText = analysisResult.summary
        ? analysisResult.summary
        : '分析完成，但未返回摘要内容，请查看右侧报告。';
      addBotMessage(`AI分析完成：\n${summaryText}`);
    } else if (analysisResult.error) {
      addBotMessage(`AI分析失败：${analysisResult.error}`);
    }
  }, [analysisResult]);

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
