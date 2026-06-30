import './CitationDemo.css'

const EVIDENCE = [
  {
    ref: 'Q2',
    label: 'Platform Analysis',
    result: '45 of 170 known attack vectors target Generative AI systems',
  },
  {
    ref: 'Q3',
    label: 'Threat Lookup',
    result: 'This technique has 3 available countermeasures and appears in 2 real incidents',
  },
  {
    ref: 'Q4',
    label: 'Defense Mapping',
    result: 'Retrieval Source Validation directly mitigates this attack vector',
  },
  {
    ref: 'Q5',
    label: 'Compliance Check',
    result: 'This defense satisfies EU AI Act Article 15 — Robustness',
  },
]

function CitationDemo() {
  return (
    <section className="section">
      <div className="container">
        <div className="citation-header">
          <h2>Verifiable Evidence</h2>
          <p className="lead">
            Every claim carries a citation marker. Click it. See the query and
            the raw results.
          </p>
        </div>

        <div className="citation-layout">
          <div className="card citation-answer">
            <div className="citation-answer-label">Agent Response</div>
            <div className="citation-text">
              RAG Poisoning <span className="citation-marker">[Q3]</span> is a known attack targeting Generative AI platforms <span className="citation-marker">[Q2]</span>. It is mitigated by Retrieval Source Validation <span className="citation-marker">[Q4]</span>, which satisfies EU AI Act Article 15 — Accuracy, Robustness and Cybersecurity <span className="citation-marker">[Q5]</span>.
            </div>
          </div>

          <div className="citation-evidence">
            {EVIDENCE.map((ev) => (
              <div key={ev.ref} className="card evidence-entry">
                <div className="evidence-header">
                  <span className="evidence-ref">[{ev.ref}]</span>
                  <span className="evidence-label">{ev.label}</span>
                </div>
                <span className="evidence-result">{ev.result}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="citation-callout">
          <p>
            Click any [Q] marker. See the Cypher query and raw results that
            produced it.
          </p>
        </div>
      </div>
    </section>
  )
}

export default CitationDemo
