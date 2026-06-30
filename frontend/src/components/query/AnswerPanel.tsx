import type { KeyboardEvent } from 'react'
import Markdown from 'react-markdown'
import rehypeRaw from 'rehype-raw'
import type { Components } from 'react-markdown'
import './AnswerPanel.css'

interface AnswerPanelProps {
  answer: string
  onCitationClick: (ref: string) => void
}

// ── Pre-process citations into HTML tags that survive markdown parsing ──

function injectCitationTags(text: string): string {
  return text.replace(
    /\[(Q\d+)\]/g,
    '<cite data-ref="$1">[$1]</cite>',
  )
}

// ── Component ──────────────────────────────────────────────

function AnswerPanel({ answer, onCitationClick }: AnswerPanelProps) {
  const processed = injectCitationTags(answer)

  function handleCitationKeyDown(
    e: KeyboardEvent<HTMLElement>,
    ref: string,
  ) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onCitationClick(ref)
    }
  }

  const components: Components = {
    cite(props) {
      const ref = (props as Record<string, unknown>)['data-ref'] as
        | string
        | undefined
      if (!ref) return <cite {...props} />

      return (
        <span
          className="answer-panel__citation"
          role="button"
          tabIndex={0}
          onClick={() => onCitationClick(ref)}
          onKeyDown={(e) => handleCitationKeyDown(e, ref)}
        >
          [{ref}]
        </span>
      )
    },
  }

  return (
    <div className="answer-panel slide-up-enter">
      <div className="card answer-panel__card">
        <div className="answer-panel__label">Agent Response</div>
        <div className="answer-panel__text">
          <Markdown rehypePlugins={[rehypeRaw]} components={components}>
            {processed}
          </Markdown>
        </div>
      </div>
    </div>
  )
}

export default AnswerPanel
