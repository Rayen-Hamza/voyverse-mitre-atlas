import './GraphBackground.css'

interface Node {
  x: number
  y: number
  size?: 'sm' | 'md' | 'lg'
  floatDuration: number
  floatDelay: number
  pulseDuration: number
  pulseDelay: number
}

interface Edge {
  from: number
  to: number
  flowDelay: number
}

const NODES: Node[] = [
  { x: 8,  y: 6,  size: 'sm', floatDuration: 8,  floatDelay: 0,   pulseDuration: 5,  pulseDelay: 0 },
  { x: 22, y: 14, size: 'md', floatDuration: 10, floatDelay: -2,  pulseDuration: 6,  pulseDelay: -1 },
  { x: 42, y: 4,  size: 'lg', floatDuration: 7,  floatDelay: -4,  pulseDuration: 4,  pulseDelay: -2 },
  { x: 68, y: 10, size: 'md', floatDuration: 9,  floatDelay: -1,  pulseDuration: 7,  pulseDelay: -3 },
  { x: 88, y: 8,  size: 'sm', floatDuration: 11, floatDelay: -3,  pulseDuration: 5,  pulseDelay: -1 },
  { x: 4,  y: 30, size: 'md', floatDuration: 8,  floatDelay: -5,  pulseDuration: 6,  pulseDelay: -4 },
  { x: 28, y: 36, size: 'lg', floatDuration: 12, floatDelay: -2,  pulseDuration: 8,  pulseDelay: -2 },
  { x: 52, y: 32, size: 'sm', floatDuration: 7,  floatDelay: -6,  pulseDuration: 5,  pulseDelay: -3 },
  { x: 78, y: 38, size: 'md', floatDuration: 10, floatDelay: -1,  pulseDuration: 7,  pulseDelay: -1 },
  { x: 94, y: 28, size: 'sm', floatDuration: 9,  floatDelay: -4,  pulseDuration: 4,  pulseDelay: -5 },
  { x: 12, y: 58, size: 'lg', floatDuration: 11, floatDelay: -3,  pulseDuration: 6,  pulseDelay: -2 },
  { x: 36, y: 64, size: 'md', floatDuration: 8,  floatDelay: -7,  pulseDuration: 5,  pulseDelay: -4 },
  { x: 58, y: 56, size: 'sm', floatDuration: 10, floatDelay: -2,  pulseDuration: 8,  pulseDelay: -1 },
  { x: 82, y: 62, size: 'lg', floatDuration: 7,  floatDelay: -5,  pulseDuration: 4,  pulseDelay: -3 },
  { x: 18, y: 82, size: 'sm', floatDuration: 9,  floatDelay: -1,  pulseDuration: 7,  pulseDelay: -2 },
  { x: 48, y: 88, size: 'md', floatDuration: 12, floatDelay: -4,  pulseDuration: 5,  pulseDelay: -5 },
  { x: 72, y: 80, size: 'lg', floatDuration: 8,  floatDelay: -6,  pulseDuration: 6,  pulseDelay: -1 },
  { x: 92, y: 86, size: 'sm', floatDuration: 10, floatDelay: -3,  pulseDuration: 4,  pulseDelay: -4 },
]

const EDGES: Edge[] = [
  { from: 0,  to: 1,  flowDelay: 0 },
  { from: 1,  to: 2,  flowDelay: -2 },
  { from: 2,  to: 3,  flowDelay: -1 },
  { from: 3,  to: 4,  flowDelay: -3 },
  { from: 5,  to: 6,  flowDelay: -1 },
  { from: 6,  to: 7,  flowDelay: -4 },
  { from: 8,  to: 9,  flowDelay: -2 },
  { from: 10, to: 11, flowDelay: -3 },
  { from: 11, to: 12, flowDelay: 0 },
  { from: 13, to: 9,  flowDelay: -1 },
  { from: 14, to: 15, flowDelay: -2 },
  { from: 16, to: 17, flowDelay: -4 },
  { from: 2,  to: 7,  flowDelay: -3 },
  { from: 6,  to: 11, flowDelay: -1 },
]

function getEdgeStyle(from: Node, to: Node) {
  const dx = to.x - from.x
  const dy = to.y - from.y
  const length = Math.sqrt(dx * dx + dy * dy)
  const angle = Math.atan2(dy, dx) * (180 / Math.PI)

  return {
    left: `${from.x}%`,
    top: `${from.y}%`,
    width: `${length}%`,
    transform: `rotate(${angle}deg)`,
  }
}

function GraphBackground() {
  return (
    <div className="graph-bg" aria-hidden="true">
      {EDGES.map((edge, i) => (
        <div
          key={`e${i}`}
          className="graph-edge"
          style={{
            ...getEdgeStyle(NODES[edge.from], NODES[edge.to]),
            animationDelay: `${edge.flowDelay}s`,
          }}
        >
          <div
            className="graph-edge-line"
            style={{ animationDelay: `${edge.flowDelay}s` }}
          />
        </div>
      ))}

      {NODES.map((node, i) => (
        <span
          key={`n${i}`}
          className={`graph-node ${node.size === 'lg' ? 'graph-node--lg' : node.size === 'sm' ? 'graph-node--sm' : ''}`}
          style={{
            left: `${node.x}%`,
            top: `${node.y}%`,
            animation: `node-float ${node.floatDuration}s ease-in-out infinite, node-pulse ${node.pulseDuration}s ease-in-out infinite`,
            animationDelay: `${node.floatDelay}s, ${node.pulseDelay}s`,
          }}
        />
      ))}
    </div>
  )
}

export default GraphBackground
