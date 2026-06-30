import './FooterCTA.css'

function FooterCTA() {
  return (
    <section className="section">
      <div className="container">
        <div className="footer-cta">
          <h2>Run Your First Query</h2>
          <p className="lead">
            Type a question about your AI system. The graph does the rest.
          </p>
          <a href="#query" className="btn btn-brand btn-lg">
            Open the Investigator
          </a>
        </div>

        <div className="footer-meta">
          <p>
            Built on MITRE ATLAS v6.0.0 &middot; Powered by Neo4j Knowledge
            Graph &middot; Voyverse AI Governance
          </p>
          <div className="footer-links">
            <a href="https://atlas.mitre.org" target="_blank" rel="noopener noreferrer">
              MITRE ATLAS
            </a>
            <a href="https://owasp.org/www-project-top-10-for-large-language-model-applications/" target="_blank" rel="noopener noreferrer">
              OWASP LLM Top 10
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}

export default FooterCTA
