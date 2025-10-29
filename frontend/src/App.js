import React, { useState } from "react";
import './App.css';
import Layout from './Layout';
import axios from 'axios';

export default function App() {
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (formData) => {
    setLoading(true);
    try {
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
          `提交成功！文件已保存：\n${response.data.path}\n可通过 ${response.data.url} 查看`
        );
      } else {
        alert("提交完成，但后端未返回 ok=true");
      }
    } catch (error) {
      console.error("提交出错：", error);
      if (error.response) {
        alert(`提交失败：${error.response.status} - ${error.response.data}`);
      } else if (error.request) {
        alert(`服务器未响应，请稍后重试。`);
      } else {
        alert("请求出错，请检查网络连接。");
      }
    } finally {
      setLoading(false);
    }
  };
  

  return (
    <div className="container">
      <header className="App-header">
        <h1>Qrent AI 租房助手</h1>
        <p>智能问卷，帮您找到理想房源</p>
      </header>
      
      <main>
        <Layout onSubmit={handleSubmit} />
        {loading && <p style={{ color: "#667eea" }}>正在提交，请稍候...</p>}
      </main>
    </div>
  );
}



