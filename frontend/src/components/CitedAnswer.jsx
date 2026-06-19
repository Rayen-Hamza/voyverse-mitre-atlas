export default function CitedAnswer({ text, onCiteClick, activeRef }) {
  const parts = text.split(/(\[Q\d+\])/g);

  return (
    <div className="leading-relaxed text-sm whitespace-pre-wrap">
      {parts.map((part, i) => {
        const match = part.match(/\[Q(\d+)\]/);
        if (match) {
          const ref = `Q${match[1]}`;
          return (
            <button
              key={i}
              onClick={() => onCiteClick(ref)}
              className={`inline-block px-1 rounded text-xs font-mono mx-0.5 ${
                activeRef === ref
                  ? "bg-blue-600 text-white"
                  : "bg-blue-100 text-blue-700 hover:bg-blue-200"
              }`}
            >
              {part}
            </button>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </div>
  );
}
