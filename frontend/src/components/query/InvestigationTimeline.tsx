import { useEffect, useRef } from 'react'
import type { ToolCallEvent } from '../../hooks/useSSEQuery'
import ToolCallCard from './ToolCallCard'
import './InvestigationTimeline.css'

interface InvestigationTimelineProps {
  toolCalls: ToolCallEvent[]
  isInvestigating: boolean
  highlightedRef: string | null
}

function InvestigationTimeline({
  toolCalls,
  isInvestigating,
  highlightedRef,
}: InvestigationTimelineProps) {
  const endRef = useRef<HTMLDivElement>(null)
  const prevCountRef = useRef(0)

  useEffect(() => {
    if (toolCalls.length > prevCountRef.current) {
      const timeout = setTimeout(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
      }, toolCalls.length * 150 + 100)
      prevCountRef.current = toolCalls.length
      return () => clearTimeout(timeout)
    }
  }, [toolCalls.length])

  if (toolCalls.length === 0 && !isInvestigating) return null

  return (
    <div className="investigation-timeline">
      <div className="investigation-timeline__label">
        Investigation Log
      </div>

      <div className="investigation-timeline__steps">
        {toolCalls.map((tc, i) => (
          <ToolCallCard
            key={tc.ref}
            toolCall={tc}
            index={i}
            isHighlighted={highlightedRef === tc.ref}
          />
        ))}

        {isInvestigating && (
          <div className="timeline-loader stagger-enter">
            <div className="timeline-step__indicator">
              <div className="timeline-loader__dot" />
            </div>
            <div className="timeline-loader__text">
              <span className="timeline-loader__cursor" />
              {toolCalls.length === 0
                ? 'Connecting to reasoning engine...'
                : 'Investigating...'}
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>
    </div>
  )
}

export default InvestigationTimeline
