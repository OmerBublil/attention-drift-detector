import { useState } from "react";
import segments from "./data/pythonReading.json";
import { api } from "./api";

function ReadingTask({ sessionId, onFinish }) {
  const [index, setIndex] = useState(0);
  const [startTime, setStartTime] = useState(performance.now());

  const handleNext = async () => {
    const now = performance.now();
    const readingTime = now - startTime;
    const text = segments[index];

    const payload = {
      session_id: sessionId,
      segment_id: index,
      text_length: text.length,
      reading_time_ms: readingTime,
    };

    console.log("Sending segment payload:", payload);

    try {
      await api.post("/segment", payload);
      console.log("Segment event sent successfully");
    } catch (error) {
      console.error("Failed to send segment event:", error);
    }

    if (index < segments.length - 1) {
      setIndex(index + 1);
      setStartTime(performance.now());
    } else {
      if (onFinish) {
        onFinish();
      }
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "40px auto" }}>
      <h2>Segment {index + 1}</h2>
      <p style={{ fontSize: "18px", lineHeight: 1.5 }}>{segments[index]}</p>
      <button
        onClick={handleNext}
        style={{ marginTop: "20px", padding: "10px 20px" }}
      >
        Next
      </button>
    </div>
  );
}

export default ReadingTask;
