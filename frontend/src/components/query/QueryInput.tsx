import { useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'
import './QueryInput.css'

interface QueryInputProps {
  onSubmit: (question: string) => void
  isDisabled: boolean
  onReset: () => void
  showReset: boolean
}

function QueryInput({
  onSubmit,
  isDisabled,
  onReset,
  showReset,
}: QueryInputProps) {
  const [value, setValue] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = value.trim()
    if (!trimmed || isDisabled) return
    onSubmit(trimmed)
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      const trimmed = value.trim()
      if (!trimmed || isDisabled) return
      onSubmit(trimmed)
    }
  }

  return (
    <div className="query-input">
      <div className="query-input__bar">
        <span className="query-input__dot" />
        <span className="query-input__dot" />
        <span className="query-input__dot" />
        <span className="query-input__title">atlas-investigator</span>
        {showReset && (
          <button
            type="button"
            className="query-input__reset"
            onClick={onReset}
          >
            New Investigation
          </button>
        )}
      </div>

      <form className="query-input__body" onSubmit={handleSubmit}>
        <span
          className={`query-input__prompt ${isDisabled ? 'query-input__prompt--busy' : ''}`}
        >
          &gt;
        </span>
        <input
          type="text"
          className="query-input__field"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your AI system's security..."
          disabled={isDisabled}
          autoFocus
        />
        <button
          type="submit"
          className="btn btn-brand query-input__submit"
          disabled={isDisabled || !value.trim()}
        >
          {isDisabled ? 'Investigating...' : 'Investigate'}
        </button>
      </form>
    </div>
  )
}

export default QueryInput
