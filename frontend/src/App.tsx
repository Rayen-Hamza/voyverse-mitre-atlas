import { useEffect, useState } from 'react'
import GraphBackground from './components/GraphBackground'
import Hero from './components/Hero'
import Stats from './components/Stats'
import ThreeLayer from './components/ThreeLayer'
import HowItWorks from './components/HowItWorks'
import ExampleQueries from './components/ExampleQueries'
import CitationDemo from './components/CitationDemo'
import FooterCTA from './components/FooterCTA'
import QueryPage from './components/query/QueryPage'

type View = 'landing' | 'query'

function getViewFromHash(): View {
  return window.location.hash === '#query' ? 'query' : 'landing'
}

function App() {
  const [view, setView] = useState<View>(getViewFromHash)

  useEffect(() => {
    function onHashChange() {
      setView(getViewFromHash())
    }
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  return (
    <>
      <GraphBackground />
      <div style={{ position: 'relative', zIndex: 1 }}>
        {view === 'landing' ? (
          <>
            <Hero />
            <hr className="section-divider" />
            <Stats />
            <hr className="section-divider" />
            <ThreeLayer />
            <hr className="section-divider" />
            <HowItWorks />
            <hr className="section-divider" />
            <ExampleQueries />
            <hr className="section-divider" />
            <CitationDemo />
            <hr className="section-divider" />
            <FooterCTA />
          </>
        ) : (
          <QueryPage />
        )}
      </div>
    </>
  )
}

export default App
