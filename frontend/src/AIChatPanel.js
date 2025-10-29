// AIChatPanel.js
import React, { useState } from "react";
import "./AIChatPanel.css";

export default function AIChatPanel() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "您好，我是您的找房助手，可以随时问我任何问题哦～" }
  ]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input.trim()) return;
    setMessages([
      ...messages,
      { role: "user", text: input },
      { role: "assistant", text: "（AI回复内容示例）" },
    ]);
    setInput("");
  };

  return (
    <div className="ai-chat-panel">
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={`chat-message ${m.role}`}>
            {m.text}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          placeholder="向AI咨询租房建议..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage}>发送</button>
      </div>
    </div>
  );
}
