import { useState } from "react";
import QueryInput from "./components/QueryInput";
import CitedAnswer from "./components/CitedAnswer";
import EvidenceCard from "./components/EvidenceCard";

const API_URL = "http://localhost:8000";

function parseSSELines(text) {
  const events = [];
  for (const line of text.split("\n")) {
    if (line.startsWith("data: ")) {
      try {
        events.push(JSON.parse(line.slice(6)));
      } catch {
        /* partial chunk — skip */
      }
    }
  }
  return events;
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [evidence, setEvidence] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeRef, setActiveRef] = useState(null);
  const [error, setError] = useState(null);

  const runQuery = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");
    setEvidence([]);
    setActiveRef(null);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        for (const event of parseSSELines(decoder.decode(value))) {
          if (event.type === "tool_call") {
            setEvidence((prev) => [...prev, event]);
          }
          if (event.type === "final_answer") {
            setAnswer(event.answer);
            setEvidence(event.evidence);
          }
          if (event.type === "error") {
            setError(event.message);
          }
        }
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <h1 className="text-lg font-semibold text-gray-800">
          ATLAS Knowledge Graph — Threat Assessment
        </h1>
        <p className="text-xs text-gray-400 mt-0.5">
          Every claim is grounded in the graph. Click any [Q] marker to see
          the evidence.
        </p>
      </div>

      <QueryInput
        question={question}
        setQuestion={setQuestion}
        onSubmit={runQuery}
        loading={loading}
      />

      {/* Main panels */}
      <div className="flex flex-1 overflow-hidden divide-x">
        {/* Left — answer */}
        <div className="flex-1 overflow-auto p-6">
          {error && (
            <div className="border border-red-300 bg-red-50 rounded p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          {loading && evidence.length > 0 && (
            <div className="border rounded p-4 bg-white mb-4">
              <p className="text-xs font-medium text-gray-400 mb-2">
                Agent investigating — {evidence.length} queries run so far
              </p>
              {evidence.slice(-3).map((e, i) => (
                <div key={i} className="text-xs text-gray-400 py-0.5">
                  {e.tool}
                </div>
              ))}
            </div>
          )}

          {answer && (
            <div className="border rounded p-5 bg-white">
              <div className="flex justify-between items-center mb-3">
                <h2 className="font-semibold text-gray-800">
                  Threat Assessment
                </h2>
                <span className="text-xs text-gray-400">
                  {evidence.length} graph queries
                </span>
              </div>
              <CitedAnswer
                text={answer}
                onCiteClick={setActiveRef}
                activeRef={activeRef}
              />
            </div>
          )}
        </div>

        {/* Right — evidence */}
        <div className="w-96 overflow-auto p-4 bg-white">
          <h2 className="font-semibold text-gray-700 mb-3 text-sm">
            Graph Evidence
            {activeRef && (
              <span className="ml-2 text-blue-600">— {activeRef}</span>
            )}
          </h2>
          <div className="space-y-2">
            {evidence.map((entry, i) => (
              <EvidenceCard
                key={i}
                entry={entry}
                isActive={activeRef === entry.ref}
                onClick={() =>
                  setActiveRef(activeRef === entry.ref ? null : entry.ref)
                }
              />
            ))}
            {evidence.length === 0 && !loading && (
              <p className="text-xs text-gray-400">
                Graph queries will appear here as the agent investigates.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
