import './ExampleQueries.css'

const EXAMPLES = [
  {
    category: 'Platform Risk',
    question: 'What are the biggest threats to my Generative AI application?',
  },
  {
    category: 'Incident Analysis',
    question: 'Show me how a real-world attack on a facial recognition system unfolded step by step.',
  },
  {
    category: 'Compliance Check',
    question: 'Which of my current defenses satisfy EU AI Act requirements?',
  },
  {
    category: 'Gap Analysis',
    question: 'Where are the blind spots in my AI system\'s security coverage?',
  },
]

function ExampleQueries() {
  return (
    <section id="examples" className="section">
      <div className="container">
        <div className="examples-header">
          <h2>Try It</h2>
        </div>

        <div className="examples-grid">
          {EXAMPLES.map((ex) => (
            <div key={ex.category} className="card example-card">
              <span className="example-category">{ex.category}</span>
              <p className="example-question">{ex.question}</p>
              <span className="example-link">
                Try this query <span className="example-arrow">&rarr;</span>
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default ExampleQueries
