import React, { useEffect, useState } from "react";
import "./App.css";
import InvitationCodeValidator from "./InvitationCodeValidator";
import ChatbotInterface from "./ChatBotInterface";
import AnalysisPanel from "./components/AnalysisPanel";
import axios from "axios";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [invitationValidated, setInvitationValidated] = useState(false);
  const [invitationCode, setInvitationCode] = useState("");
  const [remainingUses, setRemainingUses] = useState(0);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [submissionInfo, setSubmissionInfo] = useState(null);

  const handleInvitationValid = (code, remaining) => {
    setInvitationCode(code);
    setRemainingUses(remaining);
    setInvitationValidated(true);
    localStorage.setItem("qr_agent_invitation_validated", "true");
    localStorage.setItem("qr_agent_invitation_code", code);
  };

  const handleSubmit = async (formData) => {
    if (!invitationValidated || !invitationCode) {
      alert("请先验证邀请码");
      setInvitationValidated(false);
      localStorage.removeItem("qr_agent_invitation_validated");
      localStorage.removeItem("qr_agent_invitation_code");
      throw new Error("请先验证邀请码");
    }

    setLoading(true);
    setAnalysisResult(null);
    setSubmissionInfo(null);

    try {
      const reportResponse = await axios.post(
        "http://127.0.0.1:8000/limits/report/create/",
        {
          invitation_code: invitationCode,
          report_data: {
            survey_data: formData,
            submitted_at: new Date().toISOString(),
          },
        },
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
          timeout: 10000,
        }
      );

      if (reportResponse.data.status === "success") {
        setRemainingUses(reportResponse.data.remaining_uses);

        // 发送异步请求到survey端点，获取analysisId
        const response = await axios.post(
          "http://127.0.0.1:8000/survey/",
          formData,
          {
            headers: { "Content-Type": "application/json" },
            withCredentials: true,
            timeout: 5000, // 降低超时时间，因为现在是异步处理
          }
        );

        console.log("后端返回结果", response.data);

        if (response.data.ok && response.data.analysis_id) {
          const analysisId = response.data.analysis_id;
          
          // 在后台继续处理结果查询，而不是阻塞前端
          setTimeout(async () => {
            try {
              // 定期检查结果是否准备好
              const resultCheckInterval = setInterval(async () => {
                try {
                  const resultResponse = await axios.get(
                    `http://127.0.0.1:8000/survey/result/${analysisId}/`,
                    {
                      headers: { "Content-Type": "application/json" },
                      withCredentials: true,
                      timeout: 10000,
                    }
                  );
                  
                  if (resultResponse.data.ok) {
                    // 正确处理嵌套的analysis对象
                    const responseData = resultResponse.data;
                    setAnalysisResult(responseData);
                    setSubmissionInfo({
                      filename: responseData.filename || (responseData.analysis && responseData.analysis.filename),
                      path: responseData.path || (responseData.analysis && responseData.analysis.path),
                      url: responseData.url || (responseData.analysis && responseData.analysis.url),
                      remainingUses: reportResponse.data.remaining_uses,
                    });
                    clearInterval(resultCheckInterval);
                    setLoading(false);
                  } else if (resultResponse.data.error || (resultResponse.data.analysis && resultResponse.data.analysis.error)) {
                    setAnalysisResult({ 
                      ok: false, 
                      error: resultResponse.data.error || 
                             (resultResponse.data.analysis && resultResponse.data.analysis.error) 
                    });
                    clearInterval(resultCheckInterval);
                    setLoading(false);
                  }
                } catch (resultError) {
                  // 忽略单个请求错误，继续检查
                  console.warn("检查结果时出错，将继续尝试", resultError);
                }
              }, 5000); // 每5秒检查一次
              
              // 设置最大检查时间（30分钟）
              setTimeout(() => {
                clearInterval(resultCheckInterval);
                // 使用函数式更新确保获取最新状态
                setLoading(prevLoading => {
                  if (prevLoading) {
                    setAnalysisResult({ ok: false, error: "AI分析超时，请稍后手动查询结果" });
                  }
                  return false;
                });
              }, 1800000);
            } catch (backgroundError) {
              console.error("后台处理结果时出错", backgroundError);
              setLoading(false);
            }
          }, 1000);
          
          // 返回analysisId，让前端可以开始轮询进度
          return analysisId;
        } else {
          throw new Error(response.data.error || "无法获取分析ID");
        }
      } else {
        const errorMessage = `邀请码验证失败：${reportResponse.data.message}`;
        alert(errorMessage);
        setInvitationValidated(false);
        localStorage.removeItem("qr_agent_invitation_validated");
        localStorage.removeItem("qr_agent_invitation_code");
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error("提交出错", error);
      let message = "请求出错，请检查网络连接。";
      if (error.code === "ECONNABORTED") {
        message = "请求超时，请稍后重试。";
      }

      if (error.response) {
        message = `${error.response.status} - ${
          (error.response.data && error.response.data.message) ||
          error.response.data ||
          "服务器返回错误"
        }`;
        if (
          error.response.data &&
          error.response.data.message &&
          (error.response.data.message.includes("邀请码") ||
            error.response.data.status === "error")
        ) {
          setInvitationValidated(false);
          localStorage.removeItem("qr_agent_invitation_validated");
          localStorage.removeItem("qr_agent_invitation_code");
        }
      } else if (error.request) {
        message = "服务器未响应，请稍后重试。";
      }

      setAnalysisResult({ ok: false, error: message });
      setLoading(false);
      throw error; // 向上抛出错误，让ChatBotInterface能够处理
    }
  };

  useEffect(() => {
    const validated = localStorage.getItem("qr_agent_invitation_validated") === "true";
    const savedCode = localStorage.getItem("qr_agent_invitation_code");

    if (validated && savedCode) {
      axios
        .post(
          "http://127.0.0.1:8000/limits/invitation/validate/",
          { code: savedCode },
          {
            headers: { "Content-Type": "application/json" },
            withCredentials: true,
            timeout: 3000,
          }
        )
        .then((response) => {
          if (response.data.status === "success") {
            setInvitationValidated(true);
            setInvitationCode(savedCode);
            setRemainingUses(response.data.remaining_uses);
          } else {
            localStorage.removeItem("qr_agent_invitation_validated");
            localStorage.removeItem("qr_agent_invitation_code");
          }
        })
        .catch(() => {
          localStorage.removeItem("qr_agent_invitation_validated");
          localStorage.removeItem("qr_agent_invitation_code");
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
              <small>
                邀请码: {invitationCode} | 剩余使用次数: {remainingUses}
              </small>
            </div>
          </header>

          <main>
            <ChatbotInterface
              onSubmit={handleSubmit}
              analysisResult={analysisResult}
            />
            <AnalysisPanel
              result={analysisResult}
              loading={loading}
              submission={submissionInfo}
            />
            {/* 移除重复的loading提示，因为AnalysisPanel组件内部已有完整的loading状态处理 */}
          </main>
        </>
      )}
    </div>
  );
}
