// InvitationCodeValidator.js
import React, { useState } from "react";
import axios from "axios";
import "./InvitationCodeValidator.css";

export default function InvitationCodeValidator({ onValid }) {
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [remainingUses, setRemainingUses] = useState(0);

  const validateCode = async () => {
    if (!code.trim()) {
      setError("请输入邀请码");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/limits/invitation/validate/",
        { code },
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
          timeout: 5000,
        }
      );

      if (response.data.status === "success") {
        setSuccess(true);
        setRemainingUses(response.data.remaining_uses);
        // 调用父组件的回调函数，通知验证成功
        onValid(code, response.data.remaining_uses);
      } else {
        setError(response.data.message || "邀请码验证失败");
      }
    } catch (err) {
      console.error("验证邀请码时出错:", err);
      if (err.response) {
        setError(err.response.data.message || `验证失败: ${err.response.status}`);
      } else if (err.request) {
        setError("服务器未响应，请稍后重试");
      } else {
        setError("请求出错，请检查网络连接");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="invitation-validator">
      <div className="validator-container">
        <h2>请输入邀请码</h2>
        <p className="validator-description">
          为了确保服务质量，请输入有效的邀请码才能继续使用
        </p>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {success && (
          <div className="success-message">
            邀请码验证成功！剩余使用次数: {remainingUses}
          </div>
        )}
        
        <div className="input-group">
          <input
            type="text"
            placeholder="请输入邀请码（例如：QRTEST-ABC12345）"
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                validateCode();
              }
            }}
            className="code-input"
            disabled={loading || success}
          />
          <button
            onClick={validateCode}
            disabled={loading || success}
            className="validate-button"
          >
            {loading ? "验证中..." : "验证邀请码"}
          </button>
        </div>
        
        <div className="test-code-info">
          <p><strong>测试邀请码说明：</strong></p>
          <p>
            开发者可以通过运行初始化脚本生成测试邀请码，格式为 <code>QRTEST-XXXXXXXX</code>
          </p>
        </div>
      </div>
    </div>
  );
}