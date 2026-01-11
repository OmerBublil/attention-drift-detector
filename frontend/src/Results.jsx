import { useEffect, useState } from "react";
import { api } from "./api";

function Results({ sessionId, onBackToHome }) {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch summary data from backend when component mounts
  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await api.get(`/summary/${sessionId}`);
        setSummary(response.data);
      } catch (err) {
        console.error("Failed to load summary:", err);
        setError("Failed to load summary.");
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, [sessionId]);

  if (loading) {
    return (
      <div style={{ maxWidth: "600px", margin: "40px auto", fontFamily: "sans-serif" }}>
        <h2>Results</h2>
        <p>Loading summary...</p>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div style={{ maxWidth: "600px", margin: "40px auto", fontFamily: "sans-serif" }}>
        <h2>Results</h2>
        <p>{error || "No summary available."}</p>
        <button
          onClick={onBackToHome}
          style={{ marginTop: "20px", padding: "10px 20px", cursor: "pointer" }}
        >
          Back to home
        </button>
      </div>
    );
  }

  const { reading, reaction, code, concentration } = summary;

  return (
    <div style={{ maxWidth: "800px", margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>Session Results</h2>
      <p style={{ color: "#555" }}>Session ID: {summary.session_id}</p>

      {/* Overall concentration section */}
      {concentration && (
        <section style={{ marginTop: "24px" }}>
          <h3>Overall Concentration</h3>
          <p style={{ fontSize: "24px", fontWeight: "bold" }}>
            {concentration.overall_score != null
              ? `${concentration.overall_score.toFixed(1)} / 100`
              : "N/A"}
          </p>

          {/* Simple bar visualization for reading / reaction / code */}
          <div
            style={{
              marginTop: "8px",
              padding: "8px",
              borderRadius: "8px",
              backgroundColor: "#f5f5f5",
            }}
          >
            <div style={{ marginBottom: "6px" }}>Reading</div>
            <div
              style={{
                height: "8px",
                borderRadius: "4px",
                backgroundColor: "#ddd",
                marginBottom: "12px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(0, concentration.reading_score || 0)
                  )}%`,
                  height: "100%",
                  backgroundColor: "#4f81bd",
                }}
              />
            </div>

            <div style={{ marginBottom: "6px" }}>Reaction</div>
            <div
              style={{
                height: "8px",
                borderRadius: "4px",
                backgroundColor: "#ddd",
                marginBottom: "12px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(0, concentration.reaction_score || 0)
                  )}%`,
                  height: "100%",
                  backgroundColor: "#9bbb59",
                }}
              />
            </div>

            <div style={{ marginBottom: "6px" }}>Code</div>
            <div
              style={{
                height: "8px",
                borderRadius: "4px",
                backgroundColor: "#ddd",
                marginBottom: "4px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(0, concentration.code_score || 0)
                  )}%`,
                  height: "100%",
                  backgroundColor: "#c0504d",
                }}
              />
            </div>
          </div>

          {concentration.comment && (
            <p style={{ marginTop: "12px", color: "#555", lineHeight: 1.4 }}>
              {concentration.comment}
            </p>
          )}
        </section>
      )}

      {/* Reading task section */}
      <section style={{ marginTop: "24px" }}>
        <h3>Reading Task</h3>
        <ul>
          <li>Segments completed: {reading.count_segments}</li>
          <li>
            Average reading time:{" "}
            {reading.avg_reading_time_ms != null
              ? `${reading.avg_reading_time_ms.toFixed(1)} ms`
              : "N/A"}
          </li>
          <li>
            Reading time standard deviation:{" "}
            {reading.std_reading_time_ms != null
              ? `${reading.std_reading_time_ms.toFixed(1)} ms`
              : "N/A"}
          </li>
          <li>
            Fastest segment:{" "}
            {reading.min_reading_time_ms != null
              ? `${reading.min_reading_time_ms.toFixed(1)} ms`
              : "N/A"}
          </li>
          <li>
            Slowest segment:{" "}
            {reading.max_reading_time_ms != null
              ? `${reading.max_reading_time_ms.toFixed(1)} ms`
              : "N/A"}
          </li>
        </ul>
      </section>

      {/* Reaction task section */}
      <section style={{ marginTop: "24px" }}>
        <h3>Reaction Task</h3>
        <ul>
          <li>Questions completed: {reaction.count_questions}</li>
          <li>
            Average reaction time:{" "}
            {reaction.avg_reaction_time_ms != null
              ? `${reaction.avg_reaction_time_ms.toFixed(1)} ms`
              : "N/A"}
          </li>
          <li>
            Reaction time standard deviation:{" "}
            {reaction.std_reaction_time_ms != null
              ? `${reaction.std_reaction_time_ms.toFixed(1)} ms`
              : "N/A"}
          </li>
          <li>
            Fastest reaction:{" "}
            {reaction.min_reaction_time_ms != null
              ? `${reaction.min_reaction_time_ms.toFixed(1)} ms`
              : "N/A"}
          </li>
          <li>
            Slowest reaction:{" "}
            {reaction.max_reaction_time_ms != null
              ? `${reaction.max_reaction_time_ms.toFixed(1)} ms`
              : "N/A"}
          </li>
          <li>
            Accuracy:{" "}
            {reaction.accuracy != null
              ? `${(reaction.accuracy * 100).toFixed(1)}%`
              : "N/A"}
          </li>
        </ul>
      </section>

      {/* Code task section */}
      <section style={{ marginTop: "24px" }}>
        <h3>Code Task</h3>
        {code && code.count_submissions > 0 ? (
          <>
            <ul>
              <li>Submissions: {code.count_submissions}</li>
              <li>
                Overall success rate:{" "}
                {code.success_rate != null
                  ? `${(code.success_rate * 100).toFixed(1)}%`
                  : "N/A"}
              </li>
              <li>
                Average total time per submission:{" "}
                {code.avg_total_time_ms != null
                  ? `${code.avg_total_time_ms.toFixed(1)} ms`
                  : "N/A"}
              </li>
              <li>
                Average delay before first typing:{" "}
                {code.avg_first_key_delay_ms != null
                  ? `${code.avg_first_key_delay_ms.toFixed(1)} ms`
                  : "N/A"}
              </li>
              <li>
                Average typing rate:{" "}
                {code.avg_typing_rate_chars_per_sec != null
                  ? `${code.avg_typing_rate_chars_per_sec.toFixed(2)} chars/s`
                  : "N/A"}
              </li>
            </ul>

            {code.per_exercise && Object.keys(code.per_exercise).length > 0 && (
              <div style={{ marginTop: "12px" }}>
                <h4>Per-exercise breakdown</h4>
                <ul>
                  {Object.entries(code.per_exercise).map(
                    ([exerciseId, exStats]) => (
                      <li key={exerciseId}>
                        <strong>{exerciseId}</strong>:{" "}
                        {exStats.count_submissions} submissions,{" "}
                        {exStats.success_rate != null
                          ? `${(exStats.success_rate * 100).toFixed(
                              1
                            )}% success`
                          : "N/A success"},{" "}
                        {exStats.avg_total_time_ms != null
                          ? `avg time ${exStats.avg_total_time_ms.toFixed(
                              1
                            )} ms`
                          : "avg time N/A"},{" "}
                        {exStats.avg_typing_rate_chars_per_sec != null
                          ? `avg typing rate ${exStats.avg_typing_rate_chars_per_sec.toFixed(
                              2
                            )} chars/s`
                          : "avg typing rate N/A"}
                      </li>
                    )
                  )}
                </ul>
              </div>
            )}
          </>
        ) : (
          <p>No code submissions recorded for this session.</p>
        )}
      </section>

      <button
        onClick={onBackToHome}
        style={{ marginTop: "30px", padding: "10px 20px", cursor: "pointer" }}
      >
        Back to home
      </button>
    </div>
  );
}

export default Results;
