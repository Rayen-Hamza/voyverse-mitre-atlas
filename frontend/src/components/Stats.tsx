import './Stats.css'

const STATS = [
  { value: '170', label: 'Attack Techniques' },
  { value: '57', label: 'Incidents Analyzed' },
  { value: '35', label: 'Mitigations' },
  { value: '3', label: 'Frameworks Bridged' },
  { value: '16', label: 'Tactics Covered' },
]

function Stats() {
  return (
    <section className="section">
      <div className="container">
        <div className="stats-header">
          <h2>What the Graph Covers</h2>
        </div>
        <div className="stats-grid">
          {STATS.map((stat, i) => (
            <div key={stat.label} className={`card stat-card reveal reveal-d${i + 1}`}>
              <div className="stat-number">{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Stats
