export default function QueryInput({ question, setQuestion, onSubmit, loading }) {
  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="px-6 py-4 bg-white border-b flex gap-3">
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={handleKey}
        placeholder={
          "Describe your AI system or ask a security question...\n" +
          'e.g. "A RAG-based customer support chatbot using GPT-4, deployed as a public API"'
        }
        className="flex-1 border rounded p-3 text-sm resize-none h-16 focus:outline-none focus:border-blue-400"
      />
      <button
        onClick={onSubmit}
        disabled={loading || !question.trim()}
        className="px-5 py-2 bg-blue-600 text-white rounded text-sm disabled:opacity-50 hover:bg-blue-700 transition-colors self-start mt-1"
      >
        {loading ? "Investigating..." : "Assess"}
      </button>
    </div>
  );
}
