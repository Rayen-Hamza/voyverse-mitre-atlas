import './ThreeLayer.css'

function ThreeLayer() {
  return (
    <section className="section">
      <div className="container">
        <div className="three-layer-header">
          <h2>One Question. Three Answers.</h2>
        </div>

        <div className="three-layer-row">
          <div className="card layer-card">
            <h3>Threats</h3>
            <h4 className="layer-question">What can go wrong?</h4>
            <p>
              Which attacks apply to your platform — generative, agentic, or
              predictive AI.
            </p>
          </div>

          <div className="layer-connector" aria-hidden="true">
            <div className="connector-line" />
          </div>

          <div className="card layer-card">
            <h3>Risks</h3>
            <h4 className="layer-question">How bad is it?</h4>
            <p>
              Which OWASP risk categories apply and how real-world incidents
              played out.
            </p>
          </div>

          <div className="layer-connector" aria-hidden="true">
            <div className="connector-line" />
          </div>

          <div className="card layer-card">
            <h3>Compliance</h3>
            <h4 className="layer-question">Are you covered?</h4>
            <p>
              Which EU AI Act articles your defenses satisfy — and where the
              gaps are.
            </p>
          </div>
        </div>

        <div className="three-layer-footer">
          <p>
            One Cypher query traverses ATLAS, OWASP, and EU AI Act. No
            tool-switching.
          </p>
        </div>
      </div>
    </section>
  )
}

export default ThreeLayer
