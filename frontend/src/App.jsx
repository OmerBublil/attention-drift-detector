import { useState } from "react";
import ReadingTask from "./ReadingTask";
import ReactionTask from "./ReactionTask";

function App() {
  const [task, setTask] = useState(null);

  // Generate a session id once per app load
  const [sessionId] = useState(() => `session-${Date.now()}`);

  if (task === "reading") {
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

  if (task === "reaction") {
    return (
      <ReactionTask
        sessionId={sessionId}
        onFinish={() => {
          console.log("Reaction task finished. Back to main screen.");
          setTask(null);
        }}
      />
    );
  }

  return (
    <div
      style={{
        maxWidth: "600px",
        margin: "40px auto",
        fontFamily: "sans-serif",
      }}
    >
      <h1>Attention Tasks</h1>
      <p>Welcome! Choose a task to begin.</p>

      <button
        onClick={() => setTask("reading")}
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          fontSize: "16px",
          cursor: "pointer",
        }}
      >
        Start Reading + Reaction Flow
      </button>
    </div>
  );
}

export default App;
