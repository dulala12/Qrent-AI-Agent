import React, { useState } from "react";
import './App.css';
import Layout from './Layout';
import InvitationCodeValidator from './InvitationCodeValidator';
import axios from 'axios';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [invitationValidated, setInvitationValidated] = useState(false);
  const [invitationCode, setInvitationCode] = useState("");
  const [remainingUses, setRemainingUses] = useState(0);

  const handleInvitationValid = (code, remaining) => {
    setInvitationCode(code);
    setRemainingUses(remaining);
    setInvitationValidated(true);
    localStorage.setItem('qr_agent_invitation_validated', 'true');
    localStorage.setItem('qr_agent_invitation_code', code);
  };

  const handleSubmit = async (formData) => {
    setLoading(true);
    try {
      // 先检查邀请码是否有效
      if (!invitationValidated || !invitationCode) {
        alert("请先验证邀请码");
        setInvitationValidated(false);
        localStorage.removeItem('qr_agent_invitation_validated');
        return;
      }

      // 创建报告（这里会验证和使用邀请码）
      const reportResponse = await axios.post(
        "http://127.0.0.1:8000/limits/report/create/",
        {
          invitation_code: invitationCode,
          report_data: {
            survey_data: formData,
            submitted_at: new Date().toISOString()
          }
        },
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
          timeout: 10000,
        }
      );

      if (reportResponse.data.status === "success") {
        setRemainingUses(reportResponse.data.remaining_uses);
        
        // 然后调用原有的问卷提交接口
        const response = await axios.post(
          "http://127.0.0.1:8000/survey/",
          formData,
          {
            headers: { "Content-Type": "application/json" },
            withCredentials: true, 
            timeout: 8000,
          },
        );
    
        console.log("后端返回结果：", response.data);
    
        if (response.data.ok) {
          alert(
            `提交成功！文件已保存：\n${response.data.path}\n可通过 ${response.data.url} 查看\n剩余使用次数：${reportResponse.data.remaining_uses}`
          );
        } else {
          alert("提交完成，但后端未返回 ok=true");
        }
      } else {
        // 如果邀请码失效，需要重新验证
        alert(`邀请码验证失败：${reportResponse.data.message}`);
        setInvitationValidated(false);
        localStorage.removeItem('qr_agent_invitation_validated');
      }
    } catch (error) {
      console.error("提交出错：", error);
      if (error.response) {
        alert(`提交失败：${error.response.status} - ${(error.response.data && error.response.data.message) || error.response.data}`);
        // 如果是邀请码相关错误，需要重新验证
        if (error.response.data && error.response.data.message && 
            (error.response.data.message.includes('邀请码') || error.response.data.status === 'error')) {
          setInvitationValidated(false);
          localStorage.removeItem('qr_agent_invitation_validated');
        }
      } else if (error.request) {
        alert(`服务器未响应，请稍后重试。`);
      } else {
        alert("请求出错，请检查网络连接。");
      }
    } finally {
      setLoading(false);
    }
  };

  // 检查本地存储中是否有验证状态
  React.useEffect(() => {
    const validated = localStorage.getItem('qr_agent_invitation_validated') === 'true';
    const savedCode = localStorage.getItem('qr_agent_invitation_code');
    if (validated && savedCode) {
      // 重新验证邀请码是否仍然有效
      axios.post(
        "http://127.0.0.1:8000/limits/invitation/validate/",
        { code: savedCode },
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
          timeout: 3000,
        }
      ).then(response => {
        if (response.data.status === "success") {
          setInvitationValidated(true);
          setInvitationCode(savedCode);
          setRemainingUses(response.data.remaining_uses);
        } else {
          // 邀请码已失效
          localStorage.removeItem('qr_agent_invitation_validated');
          localStorage.removeItem('qr_agent_invitation_code');
        }
      }).catch(() => {
        // 验证失败，清除本地存储
        localStorage.removeItem('qr_agent_invitation_validated');
        localStorage.removeItem('qr_agent_invitation_code');
      });
    }
  }, []);

  return (
    <div className="container">
      {!invitationValidated ? (
        <InvitationCodeValidator onValid={handleInvitationValid} />
      ) : (
        <>
          <header className="App-header">
            <h1>Qrent AI 租房助手</h1>
            <p>智能问卷，帮您找到理想房源</p>
            <div className="invitation-status">
              <small>邀请码: {invitationCode} | 剩余使用次数: {remainingUses}</small>
            </div>
          </header>
          
          <main>
            <Layout onSubmit={handleSubmit} />
            {loading && <p style={{ color: "#667eea" }}>正在提交，请稍候...</p>}
          </main>
        </>
      )}
    </div>
  );
}



