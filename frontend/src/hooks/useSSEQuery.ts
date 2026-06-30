import { useCallback, useEffect, useReducer, useRef } from 'react'

// ── Types ──────────────────────────────────────────────────

export interface ToolCallEvent {
  ref: string
  tool: string
  input: Record<string, unknown>
  result: unknown
}

export type Status =
  | 'idle'
  | 'connecting'
  | 'investigating'
  | 'complete'
  | 'error'

export interface SSEState {
  status: Status
  toolCalls: ToolCallEvent[]
  answer: string | null
  evidence: ToolCallEvent[]
  error: string | null
}

type Action =
  | { type: 'SUBMIT' }
  | { type: 'TOOL_CALL'; payload: ToolCallEvent }
  | { type: 'FINAL_ANSWER'; payload: { answer: string; evidence: ToolCallEvent[] } }
  | { type: 'ERROR'; payload: string }
  | { type: 'RESET' }

// ── Reducer ────────────────────────────────────────────────

const INITIAL_STATE: SSEState = {
  status: 'idle',
  toolCalls: [],
  answer: null,
  evidence: [],
  error: null,
}

export function sseReducer(state: SSEState, action: Action): SSEState {
  switch (action.type) {
    case 'SUBMIT':
      return {
        ...INITIAL_STATE,
        status: 'connecting',
      }

    case 'TOOL_CALL':
      return {
        ...state,
        status: 'investigating',
        toolCalls: [...state.toolCalls, action.payload],
      }

    case 'FINAL_ANSWER':
      return {
        ...state,
        status: 'complete',
        answer: action.payload.answer,
        evidence: action.payload.evidence,
      }

    case 'ERROR':
      return {
        ...state,
        status: 'error',
        error: action.payload,
      }

    case 'RESET':
      return INITIAL_STATE

    default:
      return state
  }
}

// ── SSE Frame Parser ───────────────────────────────────────

function parseSSEFrames(
  buffer: string,
): { frames: Record<string, unknown>[]; remaining: string } {
  const segments = buffer.split('\n\n')
  const remaining = segments.pop() ?? ''
  const frames: Record<string, unknown>[] = []

  for (const segment of segments) {
    if (!segment.trim()) continue

    const dataLine = segment
      .split('\n')
      .find((line) => line.startsWith('data: '))

    if (!dataLine) continue

    try {
      frames.push(JSON.parse(dataLine.slice(6)) as Record<string, unknown>)
    } catch {
      if (import.meta.env.DEV) {
        console.warn('[SSE] Failed to parse frame:', dataLine)
      }
    }
  }

  return { frames, remaining }
}

// ── Hook ───────────────────────────────────────────────────

const API_BASE = import.meta.env.VITE_API_URL ?? ''

export function useSSEQuery() {
  const [state, dispatch] = useReducer(sseReducer, INITIAL_STATE)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    return () => {
      abortRef.current?.abort()
    }
  }, [])

  const submit = useCallback(async (question: string) => {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    dispatch({ type: 'SUBMIT' })

    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
        signal: controller.signal,
      })

      if (!response.ok) {
        dispatch({
          type: 'ERROR',
          payload: `Server returned ${response.status}: ${response.statusText}`,
        })
        return
      }

      const reader = response.body?.getReader()
      if (!reader) {
        dispatch({ type: 'ERROR', payload: 'No response stream available' })
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const { frames, remaining } = parseSSEFrames(buffer)
        buffer = remaining

        for (const frame of frames) {
          if (import.meta.env.DEV) {
            console.debug('[SSE]', frame.type, frame)
          }

          switch (frame.type) {
            case 'tool_call':
              dispatch({
                type: 'TOOL_CALL',
                payload: frame as unknown as ToolCallEvent,
              })
              break

            case 'final_answer':
              dispatch({
                type: 'FINAL_ANSWER',
                payload: {
                  answer: frame.answer as string,
                  evidence: frame.evidence as ToolCallEvent[],
                },
              })
              break

            case 'error':
              dispatch({
                type: 'ERROR',
                payload: (frame.message as string) ?? 'Unknown server error',
              })
              break
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === 'AbortError') return
      dispatch({
        type: 'ERROR',
        payload:
          err instanceof Error
            ? err.message
            : 'Connection failed. Is the backend running?',
      })
    }
  }, [])

  const reset = useCallback(() => {
    abortRef.current?.abort()
    abortRef.current = null
    dispatch({ type: 'RESET' })
  }, [])

  return { state, submit, reset } as const
}
