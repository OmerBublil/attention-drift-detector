import { useState } from "react";
import ReadingTask from "./ReadingTask";
import ReactionTask from "./ReactionTask";
import CodeTask from "./CodeTask";
import Results from "./Results";

function App() {
  const [task, setTask] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  // Create a new session and start the reading task
  const startNewSession = () => {
    const newId = `session-${Date.now()}`;
    setSessionId(newId);
    console.log("New session:", newId);
    setTask("reading");
  };

  const backToHome = () => {
    setTask(null);
  };

  if (task === "reading" && sessionId) {
    return (
      <ReadingTask
        sessionId={sessionId}
        onFinish={() => {
          console.log("Reading task finished. Moving to reaction task.");
          setTask("reaction");
        }}
      />
    );
  }

  if (task === "reaction" && sessionId) {
    return (
      <ReactionTask
        sessionId={sessionId}
        onFinish={() => {
          console.log("Reaction task finished. Moving to code task.");
          setTask("code");
        }}
      />
    );
  }

  if (task === "code" && sessionId) {
    return (
      <CodeTask
        sessionId={sessionId}
        onFinish={() => {
          console.log("Code task finished. Moving to results.");
          setTask("results");
        }}
      />
    );
  }

  if (task === "results" && sessionId) {
    return (
      <Results
        sessionId={sessionId}
        onBackToHome={backToHome}
      />
    );
  }

  // Home screen
  return (
    <div
      style={{
        maxWidth: "600px",
        margin: "40px auto",
        fontFamily: "sans-serif",
      }}
    >
      <h1>Attention Tasks</h1>
      <p>Welcome! Start a new session to begin the full flow.</p>

      <button
        onClick={startNewSession}
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          fontSize: "16px",
          cursor: "pointer",
        }}
      >
        Start Reading + Reaction + Code
      </button>

      {sessionId && (
        <p style={{ marginTop: "16px", fontSize: "12px", color: "#555" }}>
          Last session ID: {sessionId}
        </p>
      )}
    </div>
  );
}

export default App;
