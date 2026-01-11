import { useState, useEffect } from "react";
import { api } from "./api";

// Simple Python exercises without the solution filled in
const EXERCISES = [
  {
    id: "add_two",
    title: "Exercise 1: add_two",
    description:
      "Write a function add_two(x) that returns the input number plus 2.",
    starterCode: `def add_two(x):
    # TODO: return x plus 2
    pass
`,
  },
  {
    id: "reverse_string",
    title: "Exercise 2: reverse_string",
    description:
      "Write a function reverse_string(s) that returns the reversed string.",
    starterCode: `def reverse_string(s):
    # TODO: reverse the string and return it
    pass
`,
  },
  {
    id: "sum_list",
    title: "Exercise 3: sum_list",
    description:
      "Write a function sum_list(lst) that returns the sum of all items in the list.",
    starterCode: `def sum_list(lst):
    # TODO: return the sum of all items in lst
    pass
`,
  },
];

function CodeTask({ sessionId, onFinish }) {
  const [index, setIndex] = useState(0);
  const [code, setCode] = useState(EXERCISES[0].starterCode);
  const [startTime, setStartTime] = useState(performance.now());
  const [firstKeyTime, setFirstKeyTime] = useState(null);
  const [status, setStatus] = useState("idle"); // "idle" | "running" | "success" | "error"
  const [feedback, setFeedback] = useState("");

  // Reset state when moving to a new exercise
  useEffect(() => {
    setCode(EXERCISES[index].starterCode);
    setStartTime(performance.now());
    setFirstKeyTime(null);
    setStatus("idle");
    setFeedback("");
  }, [index]);

  const handleCodeChange = (e) => {
    const value = e.target.value;
    setCode(value);

    // Capture the very first time the user starts typing
    if (firstKeyTime === null) {
      setFirstKeyTime(performance.now());
    }
  };

  const handleKeyDown = (e) => {
    // Handle Tab key to insert spaces instead of changing focus
    if (e.key === "Tab") {
      e.preventDefault();

      const tab = "    "; // 4 spaces
      const target = e.target;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      const value = target.value;

      const newValue =
        value.slice(0, start) + tab + value.slice(end);

      setCode(newValue);

      // Restore caret position after inserting the spaces
      // Using requestAnimationFrame to wait for React to apply the new value
      requestAnimationFrame(() => {
        target.selectionStart = target.selectionEnd = start + tab.length;
      });
    }
  };

  const handleRun = async () => {
    setStatus("running");
    setFeedback("");

    const now = performance.now();
    const totalTime = now - startTime;
    const firstKeyDelay =
      firstKeyTime !== null ? firstKeyTime - startTime : null;
    const eventTime = Date.now();

    const exercise = EXERCISES[index];

    // New: typing metrics
    const starterCode = exercise.starterCode || "";
    const starterLength = starterCode.length;
    const codeLength = code.length;

    let typingDuration = null;
    if (firstKeyTime !== null) {
      typingDuration = now - firstKeyTime;
    }

    const payload = {
      session_id: sessionId,
      exercise_id: exercise.id,
      code: code,
      total_time_ms: totalTime,
      first_key_delay_ms: firstKeyDelay,
      client_timestamp_ms: eventTime,
      code_length: codeLength,
      starter_code_length: starterLength,
      typing_duration_ms: typingDuration,
    };

    console.log("Sending code submission:", payload);

    try {
      const response = await api.post("/code", payload);
      const data = response.data;

      if (data.is_correct) {
        setStatus("success");
        setFeedback(
          `All tests passed! (${data.tests_passed} passed, ${data.tests_failed} failed)`
        );
      } else {
        setStatus("error");
        if (data.error) {
          setFeedback(
            `Tests did not all pass. Error: ${data.error} (passed: ${data.tests_passed}, failed: ${data.tests_failed})`
          );
        } else {
          setFeedback(
            `Tests did not all pass. (passed: ${data.tests_passed}, failed: ${data.tests_failed})`
          );
        }
      }
    } catch (error) {
      console.error("Failed to send code submission:", error);
      setStatus("error");
      setFeedback("Failed to submit code to backend.");
    }
  };


  const handleNextExercise = () => {
    if (index < EXERCISES.length - 1) {
      setIndex(index + 1);
    } else {
      onFinish();
    }
  };

  const exercise = EXERCISES[index];

  return (
    <div style={{ maxWidth: "800px", margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>Code Task</h2>
      <h3>{exercise.title}</h3>
      <p style={{ marginBottom: "12px" }}>{exercise.description}</p>

      <textarea
        value={code}
        onChange={handleCodeChange}
        onKeyDown={handleKeyDown}
        style={{
          width: "100%",
          height: "240px",
          fontFamily: "monospace",
          fontSize: "14px",
          padding: "8px",
          boxSizing: "border-box",
        }}
      />

      <div style={{ marginTop: "16px", display: "flex", gap: "12px" }}>
        <button
          onClick={handleRun}
          disabled={status === "running"}
          style={{ padding: "8px 16px", cursor: "pointer" }}
        >
          {status === "running" ? "Running..." : "Run tests"}
        </button>

        <button
          onClick={handleNextExercise}
          disabled={status === "running"}
          style={{ padding: "8px 16px", cursor: "pointer" }}
        >
          {index < EXERCISES.length - 1 ? "Next exercise" : "Finish task"}
        </button>
      </div>

      {feedback && (
        <p
          style={{
            marginTop: "16px",
            whiteSpace: "pre-wrap",
            color: status === "success" ? "green" : "red",
          }}
        >
          {feedback}
        </p>
      )}
    </div>
  );
}

export default CodeTask;
