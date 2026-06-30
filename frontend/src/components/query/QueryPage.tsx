import { useCallback, useEffect, useRef, useState } from 'react'
import { useSSEQuery } from '../../hooks/useSSEQuery'
import QueryInput from './QueryInput'
import SuggestedQueries from './SuggestedQueries'
import InvestigationTimeline from './InvestigationTimeline'
import AnswerPanel from './AnswerPanel'
import './QueryPage.css'

function QueryPage() {
  const { state, submit, reset } = useSSEQuery()
  const [highlightedRef, setHighlightedRef] = useState<string | null>(null)
  const highlightTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    return () => {
      if (highlightTimeoutRef.current) {
        clearTimeout(highlightTimeoutRef.current)
      }
    }
  }, [])

  const handleCitationClick = useCallback((ref: string) => {
    if (highlightTimeoutRef.current) {
      clearTimeout(highlightTimeoutRef.current)
    }
    setHighlightedRef(ref)
    highlightTimeoutRef.current = setTimeout(() => {
      setHighlightedRef(null)
    }, 3000)
  }, [])

  const handleSubmit = useCallback(
    (question: string) => {
      submit(question)
    },
    [submit],
  )

  const handleReset = useCallback(() => {
    reset()
    setHighlightedRef(null)
    if (highlightTimeoutRef.current) {
      clearTimeout(highlightTimeoutRef.current)
    }
  }, [reset])

  const isIdle = state.status === 'idle'
  const isActive =
    state.status === 'connecting' || state.status === 'investigating'
  const isComplete = state.status === 'complete'
  const isError = state.status === 'error'

  const layoutClass = isIdle
    ? 'query-page--idle'
    : 'query-page--active'

  return (
    <section className={`query-page ${layoutClass}`}>
      <div className="container">
        <div className="query-page__nav">
          <a href="#" className="query-page__back">
            &larr; Back
          </a>
        </div>

        <div className="query-page__input-area reveal">
          <QueryInput
            onSubmit={handleSubmit}
            isDisabled={isActive}
            onReset={handleReset}
            showReset={isComplete || isError}
          />
        </div>

        {isIdle && (
          <div className="query-page__suggestions">
            <SuggestedQueries onSelect={handleSubmit} />
          </div>
        )}

        {(isActive || isComplete) && (
          <div className="query-page__timeline">
            <InvestigationTimeline
              toolCalls={state.toolCalls}
              isInvestigating={isActive}
              highlightedRef={highlightedRef}
            />
          </div>
        )}

        {isComplete && state.answer && (
          <div className="query-page__answer">
            <AnswerPanel
              answer={state.answer}
              onCitationClick={handleCitationClick}
            />
          </div>
        )}

        {isError && (
          <div className="query-page__error stagger-enter">
            <div className="card query-page__error-card">
              <span className="query-page__error-icon">!</span>
              <div className="query-page__error-content">
                <div className="query-page__error-title">
                  Investigation Failed
                </div>
                <div className="query-page__error-message">
                  {state.error}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

export default QueryPage
