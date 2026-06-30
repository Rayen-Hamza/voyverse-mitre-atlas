import { EXAMPLE_QUERIES } from '../../data/exampleQueries'
import './SuggestedQueries.css'

interface SuggestedQueriesProps {
  onSelect: (question: string) => void
}

function SuggestedQueries({ onSelect }: SuggestedQueriesProps) {
  return (
    <div className="suggested-queries">
      <div className="suggested-queries__label">Try an example</div>
      <div className="suggested-queries__grid">
        {EXAMPLE_QUERIES.map((example, i) => (
          <button
            key={example.category}
            type="button"
            className="card suggested-queries__card stagger-enter"
            style={{ animationDelay: `${(i + 1) * 100}ms` }}
            onClick={() => onSelect(example.question)}
          >
            <span className="suggested-queries__category">
              {example.category}
            </span>
            <span className="suggested-queries__question">
              {example.question}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}

export default SuggestedQueries
