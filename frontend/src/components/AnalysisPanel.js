import React from "react";

export default function AnalysisPanel({ result, loading, submission }) {
  if (loading && !result) {
    return (
      <section className="analysis-panel">
        <h2>AI 分析报告</h2>
        <p className="analysis-status">AI 正在根据最新表单生成分析，请稍候…</p>
      </section>
    );
  }

  if (!result) {
    return null;
  }

  // 获取分析数据，处理嵌套的analysis对象
  const analysisData = result.analysis || result;
  const isSuccessful = result.ok && !analysisData.error;
  
  return (
    <section className="analysis-panel">
      <h2>AI 分析报告</h2>
      {submission && (
        <div className="analysis-meta">
          <p>
            数据文件：<span>{submission.filename}</span>
          </p>
          <p>
            存储路径：<code>{submission.path}</code>
          </p>
          {submission.remainingUses !== undefined && (
            <p>邀请码剩余次数：{submission.remainingUses}</p>
          )}
        </div>
      )}
      {!isSuccessful ? (
        <p className="analysis-error">
          未能生成 AI 报告：{analysisData.error || result.error || "请稍后再试。"}
        </p>
      ) : (
        <>
          {analysisData.summary ? (
            <div className="analysis-summary">
              <h3>分析摘要</h3>
              <pre>{analysisData.summary}</pre>
            </div>
          ) : (
            <p className="analysis-status">AI 未返回摘要内容。</p>
          )}
          {analysisData.report_markdown && (
            <details className="analysis-details" open>
              <summary>查看完整报告</summary>
              <div className="report-content">
                <pre>{analysisData.report_markdown}</pre>
              </div>
            </details>
          )}
          {analysisData.tasks && analysisData.tasks.length > 0 && (
            <details className="analysis-details">
              <summary>任务详情</summary>
              <div className="tasks-content">
                {analysisData.tasks.map((task, index) => (
                  <div key={index} className="task-item">
                    <h4>{task.task_name || `任务 ${index + 1}`}</h4>
                    {task.description && <p><strong>描述：</strong>{task.description}</p>}
                    {task.output && <p><strong>输出：</strong><pre>{task.output}</pre></p>}
                    {task.status && <p><strong>状态：</strong>{task.status}</p>}
                  </div>
                ))}
              </div>
            </details>
          )}
        </>
      )}
    </section>
  );
}
