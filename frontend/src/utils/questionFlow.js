const questionFlow = {
    
    university: {
      next: 'budget',
      botMessage: '好的请选择您的目标大学👇',
      options: ['新南威尔士大学（UNSW）', '悉尼大学（USYD）', '悉尼科技大学（UTS）']
    },
  
    
    budget: {
      next: 'includeBills',
      botMessage: '**第 2 步：预算与费用**\n\n请告诉我您的预算范围（单位：澳元/周）',
      options: [
        { type: 'input', label: '最低预算', placeholder: '例如：300', unit: '澳元/周', key: 'minBudget' },
        { type: 'input', label: '最高预算', placeholder: '例如：500', unit: '澳元/周', key: 'maxBudget' }
      ],
    },
  
    
    includeBills: {
      next: 'commuteTime',
      botMessage: '好的，明白了！那这个预算是否包含 Bills（水电网费）呢？',
      options: ['包含', '不包含', '不确定']
    },
  
    
    commuteTime: {
      next: 'roomType',
      botMessage: '好的！那您可以接受的通勤时间上限是多少呢？',
      options: ['15 分钟', '30 分钟', '45 分钟', '1 小时', '无限制']
    },
  
    
    roomType: {
      next: 'moveInDate',
      botMessage: '**第 3 步：房型与合租意向**\n\n关于房型，您有什么偏好吗？',
      options: ['Studio', '一居室', '两居室', '三居室及以上', '单间（合租）', '不确定']
    },
  
    
    moveInDate: {
      next: 'leaseTerm',
      botMessage: '**第 4 步：租期与入住时间**\n\n明白了！那您最早什么时候可以入住呢？',
      type: 'date'
    },
  
    
    leaseTerm: {
      next: 'flexibility',
      botMessage: '好的！您期望的租期是多久？',
      options: ['6 个月', '12 个月', '其他']
    },
  
    
    flexibility: {
      next: 'complete',
      botMessage: '**第 5 步：灵活性与偏好确认**\n\n最后一个问题！为了在预算内找到最佳房源，您愿意在哪些方面保持灵活？（可多选）',
      multiSelect: true,
      options: [
        '可以接受稍小的房间面积',
        '可以接受略旧的装修',
        '可以接受离交通枢纽稍远（如多步行 5-10 分钟）',
        '可以接受不含部分 Bills',
        '对上述条件均不妥协'
      ]
    },
  
    
    complete: {
      botMessage: '太好了！我已经收集完您的所有需求了。让我为您总结一下...'
    }
  };
  
  export default questionFlow;
  