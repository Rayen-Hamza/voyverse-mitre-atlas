import { useEffect, useRef, useState } from 'react'
import type { ToolCallEvent } from '../../hooks/useSSEQuery'
import './ToolCallCard.css'

// ── Props ──────────────────────────────────────────────────

interface ToolCallCardProps {
  toolCall: ToolCallEvent
  index: number
  isHighlighted: boolean
}

// ── Input summary helper ───────────────────────────────────

function summarizeToolInput(
  tool: string,
  input: Record<string, unknown>,
): string {
  switch (tool) {
    case 'get_physical_schema':
      return 'Schema introspection'

    case 'count_and_summarize': {
      const label = input.label as string | undefined
      const prop = input.property_name as string | undefined
      return prop ? `Count ${label} by ${prop}` : `Count ${label ?? 'nodes'}`
    }

    case 'get_node_neighbors': {
      const nodeId = input.node_id as string | undefined
      const rel = input.relationship_type as string | undefined
      return rel
        ? `Neighbors of ${nodeId} via ${rel}`
        : `Neighbors of ${nodeId}`
    }

    case 'read_neo4j_cypher': {
      const query = input.query as string | undefined
      if (!query) return 'Cypher query'
      const trimmed = query.replace(/\s+/g, ' ').trim()
      return trimmed.length > 60 ? trimmed.slice(0, 57) + '...' : trimmed
    }

    case 'find_paths_between': {
      const src = input.source_id as string | undefined
      const tgt = input.target_id as string | undefined
      return `${src ?? '?'} → ${tgt ?? '?'}`
    }

    default: {
      const str = JSON.stringify(input)
      return str.length > 60 ? str.slice(0, 57) + '...' : str
    }
  }
}

// ── Friendly tool name ─────────────────────────────────────

function formatToolName(tool: string): string {
  switch (tool) {
    case 'get_physical_schema':
      return 'Schema Discovery'
    case 'count_and_summarize':
      return 'Data Analysis'
    case 'get_node_neighbors':
      return 'Graph Traversal'
    case 'read_neo4j_cypher':
      return 'Cypher Query'
    case 'find_paths_between':
      return 'Path Finding'
    default:
      return tool
  }
}

// ── Component ──────────────────────────────────────────────

function ToolCallCard({ toolCall, index, isHighlighted }: ToolCallCardProps) {
  const [expanded, setExpanded] = useState(false)
  const cardRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isHighlighted) {
      setExpanded(true)
      cardRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [isHighlighted])

  const summary = summarizeToolInput(toolCall.tool, toolCall.input)
  const friendlyName = formatToolName(toolCall.tool)

  return (
    <div
      className="timeline-step stagger-enter"
      style={{ animationDelay: `${index * 150}ms` }}
      data-ref={toolCall.ref}
    >
      <div className="timeline-step__indicator">
        <div className="timeline-step__badge">{toolCall.ref}</div>
        <div className="timeline-step__line" />
      </div>

      <div
        ref={cardRef}
        className={`card tool-call-card ${isHighlighted ? 'tool-call-card--highlighted' : ''}`}
        id={`evidence-${toolCall.ref}`}
      >
        <button
          type="button"
          className="tool-call-card__header"
          onClick={() => setExpanded((prev) => !prev)}
          aria-expanded={expanded}
          aria-controls={`detail-${toolCall.ref}`}
        >
          <span className="tool-call-card__ref">[{toolCall.ref}]</span>
          <span className="tool-call-card__name">{friendlyName}</span>
          <span className="tool-call-card__summary">{summary}</span>
          <span
            className={`tool-call-card__chevron ${expanded ? 'tool-call-card__chevron--open' : ''}`}
          >
            &#9662;
          </span>
        </button>

        {expanded && (
          <div className="tool-call-card__detail" id={`detail-${toolCall.ref}`}>
            <div className="tool-call-card__section">
              <div className="tool-call-card__section-label">Input</div>
              <pre className="tool-call-card__code">
                <code>{JSON.stringify(toolCall.input, null, 2)}</code>
              </pre>
            </div>
            <div className="tool-call-card__section">
              <div className="tool-call-card__section-label">Result</div>
              <pre className="tool-call-card__code">
                <code>{JSON.stringify(toolCall.result, null, 2)}</code>
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ToolCallCard
