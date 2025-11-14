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
      {!result.ok ? (
        <p className="analysis-error">
          未能生成 AI 报告：{result.error || "请稍后再试。"}
        </p>
      ) : (
        <>
          {result.summary ? (
            <pre className="analysis-summary">{result.summary}</pre>
          ) : (
            <p className="analysis-status">AI 未返回摘要内容。</p>
          )}
          {result.report_markdown && (
            <details className="analysis-details" open>
              <summary>查看完整报告</summary>
              <pre>{result.report_markdown}</pre>
            </details>
          )}
        </>
      )}
    </section>
  );
}
