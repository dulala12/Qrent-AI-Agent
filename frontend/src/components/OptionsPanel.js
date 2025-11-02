import { useState } from 'react';
import '../chatBot.css';

const OptionsPanel = ({ options, multiSelect, onOptionClick, onMultiSelectConfirm }) => {
  const [selected, setSelected] = useState([]);

  if (multiSelect) {
    const toggleOption = (option) => {
      setSelected(prev =>
        prev.includes(option)
          ? prev.filter(item => item !== option)
          : [...prev, option]
      );
    };

    return (
      <div className="options-panel">
        <div className="multi-select-options">
          {options.map((option, idx) => (
            <button
              key={idx}
              onClick={() => toggleOption(option)}
              className={`multi-select-option ${selected.includes(option) ? 'selected' : ''}`}
            >
              <div className="checkbox">
                {selected.includes(option) && (
                  <svg viewBox="0 0 24 24">
                    <path
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </div>
              <span className="option-text">{option}</span>
            </button>
          ))}
        </div>
        <button
          onClick={() => onMultiSelectConfirm(selected)}
          className="multi-select-confirm"
        >
          确认选择
        </button>
      </div>
    );
  }

  // 单选选项
  return (
    <div className="options-panel">
      <div className="options-grid">
        {options.map((option, idx) => (
          <button
            key={idx}
            onClick={() => onOptionClick(option)}
            className="option-btn"
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
};

export default OptionsPanel;
