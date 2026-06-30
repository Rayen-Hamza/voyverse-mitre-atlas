import './Hero.css'

function Hero() {
  return (
    <section className="hero">
      <div className="hero-content">
        <p className="hero-status reveal">
          <span className="hero-status-prefix">$</span> atlas-kg
          <span className="hero-status-sep">&mdash;</span>
          <span className="hero-status-live">ready</span>
        </p>

        <h1 className="reveal reveal-d1">
          Threat Intelligence<br />for AI Systems
        </h1>

        <p className="lead reveal reveal-d2">
          Describe your AI system. Get a threat assessment with real incident
          data, OWASP risk mappings, and EU AI Act compliance — every claim
          cited to its source.
        </p>

        <div className="hero-terminal reveal reveal-d3">
          <div className="hero-terminal-bar">
            <span className="hero-terminal-dot" />
            <span className="hero-terminal-dot" />
            <span className="hero-terminal-dot" />
            <span className="hero-terminal-title">atlas-investigator</span>
          </div>
          <div className="hero-terminal-body">
            <span className="hero-terminal-prompt">&gt;</span>
            <span className="hero-terminal-typing">
              How secure is my Generative AI deployment?
            </span>
          </div>
        </div>

        <div className="hero-cta reveal reveal-d4">
          <a href="#query" className="btn btn-brand btn-lg">
            Start Investigating
          </a>
          <a href="#how-it-works" className="btn btn-ghost btn-lg">
            See How It Works
          </a>
        </div>
      </div>
    </section>
  )
}

export default Hero
