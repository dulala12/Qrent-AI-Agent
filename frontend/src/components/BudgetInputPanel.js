import { useState } from 'react';
import '../chatBot.css';

const BudgetInputPanel = ({ onConfirm }) => {
  const [minBudget, setMinBudget] = useState('');
  const [maxBudget, setMaxBudget] = useState('');

  const handleConfirm = () => {
    if (!minBudget || !maxBudget) {
      alert('请填写完整的预算范围');
      return;
    }
    onConfirm(minBudget, maxBudget);
  };

  return (
    <div className="budget-panel">
      <div className="budget-inputs">
        <div className="budget-input-group">
          <label>最低预算</label>
          <div className="budget-input-wrapper">
            <input
              type="number"
              value={minBudget}
              onChange={(e) => setMinBudget(e.target.value)}
              placeholder="300"
            />
            <span className="budget-unit">澳元/周</span>
          </div>
        </div>

        <div className="budget-input-group">
          <label>最高预算</label>
          <div className="budget-input-wrapper">
            <input
              type="number"
              value={maxBudget}
              onChange={(e) => setMaxBudget(e.target.value)}
              placeholder="500"
            />
            <span className="budget-unit">澳元/周</span>
          </div>
        </div>
      </div>

      <button onClick={handleConfirm} className="confirm-btn">
        确认
      </button>
    </div>
  );
};

export default BudgetInputPanel;
