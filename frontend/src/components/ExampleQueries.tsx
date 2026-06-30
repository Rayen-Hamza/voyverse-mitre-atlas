import { EXAMPLE_QUERIES } from '../data/exampleQueries'
import './ExampleQueries.css'

function ExampleQueries() {
  return (
    <section id="examples" className="section">
      <div className="container">
        <div className="examples-header">
          <h2>Try It</h2>
        </div>

        <div className="examples-grid">
          {EXAMPLE_QUERIES.map((ex) => (
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
