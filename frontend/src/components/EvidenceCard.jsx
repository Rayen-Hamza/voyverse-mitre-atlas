export default function EvidenceCard({ entry, isActive, onClick }) {
  return (
    <div
      onClick={onClick}
      className={`border rounded p-3 cursor-pointer text-sm transition-all ${
        isActive
          ? "border-blue-500 bg-blue-50"
          : "border-gray-200 hover:border-gray-400"
      }`}
    >
      <div className="flex justify-between items-center mb-1">
        <span className="font-mono text-xs font-bold text-blue-600">
          {entry.ref}
        </span>
        <span className="text-xs text-gray-400">{entry.tool}</span>
      </div>

      {entry.input?.query ? (
        <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-x-auto whitespace-pre-wrap">
          {entry.input.query}
        </pre>
      ) : (
        <div className="text-xs text-gray-500 mt-1">
          {JSON.stringify(entry.input).slice(0, 80)}
          {JSON.stringify(entry.input).length > 80 ? "..." : ""}
        </div>
      )}

      <div className="mt-1 text-xs text-gray-400">
        {Array.isArray(entry.result?.records)
          ? `${entry.result.records.length} records`
          : "Structured result"}
      </div>

      {isActive && (
        <pre className="mt-2 text-xs bg-gray-50 p-2 rounded overflow-auto max-h-64 border">
          {JSON.stringify(entry.result, null, 2)}
        </pre>
      )}
    </div>
  );
}
