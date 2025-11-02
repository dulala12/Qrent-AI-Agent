const getInputPlaceholder = (currentQuestion) => {
    const placeholders = {
      locationOther: '输入您的目标大学名称...',
      moveInDate: '选择入住日期 (例如：2024-12-01)...',
      leaseTermOther: '输入您期望的租期...',
    };
    return placeholders[currentQuestion] || '输入您的回答...';
  };
  
  export function generateSummary(formData) {
    const parts = [];
  
    if (formData.university) parts.push(`🎓 **目标大学**：${formData.university}`);
    if (formData.minBudget || formData.maxBudget)
      parts.push(`💰 **预算**：${formData.minBudget || '?'} - ${formData.maxBudget || '?'} 澳元/周`);
    if (formData.includeBills) parts.push(`📋 **是否含Bills**：${formData.includeBills}`);
    if (formData.commuteTime) parts.push(`🚗 **通勤时间**：${formData.commuteTime}`);
    if (formData.roomType) parts.push(`🏠 **房型偏好**：${formData.roomType}`);
    if (formData.moveInDate) parts.push(`📅 **入住日期**：${formData.moveInDate}`);
    if (formData.leaseTerm) parts.push(`⏰ **租期**：${formData.leaseTerm}`);
    if (formData.flexibility?.length)
      parts.push(`🎯 **灵活性**：${formData.flexibility.join('、')}`);
  
    return `
  ✨ **您的租房需求总结**
  
  ${parts.join('\n')}
  
  ---
  
  太棒了！根据您的需求，我现在就开始为您搜索合适的房源。请稍等片刻...
  `;
  }
  
  
  
  
  const getInitialMessages = () => [
    {
      id: 1,
      type: 'bot',
      content: '您好！我是您的租房助手 🏠 我会通过几个简单的问题来了解您的租房需求，帮您找到最合适的房源。',
      timestamp: new Date()
    },
    {
      id: 2,
      type: 'bot',
      content: '让我们开始吧！首先，我想了解一下您的预算情况。',
      timestamp: new Date()
    },
    {
      id: 3,
      type: 'bot',
      content: '您好！我是您的租房助手 🏡 我将通过几个问题帮您匹配最合适的房源。\n\n首先，请告诉我您的目标大学是哪一所？',
      options: ['新南威尔士大学（UNSW）', '悉尼大学（USYD）', '悉尼科技大学（UTS）'],
      question: 'university',
      timestamp: new Date()
    }
  ];
  
  const chatbotUtils = {
    getInputPlaceholder,
    generateSummary,
    getInitialMessages,
  };
  
  export default chatbotUtils;