import GraphBackground from './components/GraphBackground'
import Hero from './components/Hero'
import Stats from './components/Stats'
import ThreeLayer from './components/ThreeLayer'
import HowItWorks from './components/HowItWorks'
import ExampleQueries from './components/ExampleQueries'
import CitationDemo from './components/CitationDemo'
import FooterCTA from './components/FooterCTA'

function App() {
  return (
    <>
      <GraphBackground />
      <div style={{ position: 'relative', zIndex: 1 }}>
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
      </div>
    </>
  )
}

export default App
