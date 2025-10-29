import React from "react";
import Questionnaire from "./Questionnaire";
import AIChatPanel from "./AIChatPanel";
import "./Questionnaire.css";

export default function QuestionnaireLayout({ onSubmit }) {
  return (
    <div className="layout-container">
      <div className="left-panel">
        <Questionnaire onSubmit={onSubmit} />
      </div>
      <div className="right-panel">
        <AIChatPanel />
      </div>
    </div>
  );
}
