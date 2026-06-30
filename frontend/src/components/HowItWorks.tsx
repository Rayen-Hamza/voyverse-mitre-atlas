import './HowItWorks.css'

const STEPS = [
  {
    number: '01',
    title: 'Ask',
    desc: 'Describe your AI system or ask a security question in plain language.',
    tag: 'Natural Language',
  },
  {
    number: '02',
    title: 'Investigate',
    desc: 'The agent runs Cypher queries against the graph. You see every query and result as it happens.',
    tag: 'Live Graph Traversal',
  },
  {
    number: '03',
    title: 'Verify',
    desc: 'Every claim in the answer links to its source. Click any citation to see the data behind it.',
    tag: 'Cited Evidence',
  },
]

function HowItWorks() {
  return (
    <section id="how-it-works" className="section">
      <div className="container">
        <div className="how-header">
          <h2>How It Works</h2>
          <p className="lead">
            Three steps. No setup.
          </p>
        </div>

        <div className="how-steps">
          {STEPS.map((step) => (
            <div key={step.number} className="how-step">
              <div className="how-step-indicator">
                <div className="how-step-number">{step.number}</div>
                <div className="how-step-line" />
              </div>
              <div className="how-step-content">
                <div className="how-step-title">{step.title}</div>
                <p className="how-step-desc">{step.desc}</p>
                <span className="how-tag">{step.tag}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default HowItWorks
