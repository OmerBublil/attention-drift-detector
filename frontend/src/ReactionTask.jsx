import { useState } from "react";
import questions from "./data/pythonQuestions.json";
import { api } from "./api";

function ReactionTask({ sessionId, onFinish }) {
  const [index, setIndex] = useState(0);
  const [startTime, setStartTime] = useState(performance.now());

  const handleAnswer = async (optionIndex) => {
    const now = performance.now();
    const reactionTime = now - startTime;
    const question = questions[index];
    const isCorrect = optionIndex === question.correctIndex;
    const eventTime = Date.now(); // absolute timestamp in ms

    const payload = {
      session_id: sessionId,
      question_index: index,
      reaction_time_ms: reactionTime,
      is_correct: isCorrect,
      client_timestamp_ms: eventTime,
      chosen_option_index: optionIndex,
    };

    console.log("Sending reaction payload:", payload);

    try {
      await api.post("/reaction", payload);
      console.log("Reaction event sent successfully");
    } catch (error) {
      console.error("Failed to send reaction event:", error);
    }

    if (index < questions.length - 1) {
      setIndex(index + 1);
      setStartTime(performance.now());
    } else {
      onFinish();
    }
  };

  const q = questions[index];

  return (
    <div style={{ maxWidth: "600px", margin: "40px auto" }}>
      <h2>Question {index + 1}</h2>

      <p style={{ fontSize: "18px", marginBottom: "16px" }}>{q.prompt}</p>

      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {q.options.map((opt, i) => (
          <button
            key={i}
            onClick={() => handleAnswer(i)}
            style={{ padding: "10px 16px", cursor: "pointer" }}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  );
}

export default ReactionTask;
