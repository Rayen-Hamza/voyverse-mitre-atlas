import { useEffect, useRef } from 'react'
import './GraphBackground.css'

declare global {
  interface Window {
    VANTA?: {
      NET: (opts: Record<string, unknown>) => { destroy: () => void }
    }
  }
}

function initVanta(el: HTMLElement): { destroy: () => void } | null {
  if (!window.VANTA) return null

  return window.VANTA.NET({
    el,
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    minHeight: 200.0,
    minWidth: 200.0,
    scale: 1.0,
    scaleMobile: 1.0,
    color: 0x389dc6,
    backgroundColor: 0x020804,
    points: 10.0,
    maxDistance: 23.0,
    spacing: 18.0,
  })
}

function GraphBackground() {
  const containerRef = useRef<HTMLDivElement>(null)
  const effectRef = useRef<{ destroy: () => void } | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const el = containerRef.current
    effectRef.current = initVanta(el)

    if (effectRef.current) return

    // Scripts might still be loading — poll until VANTA is available
    const interval = setInterval(() => {
      if (window.VANTA && !effectRef.current) {
        effectRef.current = initVanta(el)
        if (effectRef.current) clearInterval(interval)
      }
    }, 100)

    return () => {
      clearInterval(interval)
      if (effectRef.current) {
        effectRef.current.destroy()
        effectRef.current = null
      }
    }
  }, [])

  return <div ref={containerRef} className="vanta-bg" />
}

export default GraphBackground
