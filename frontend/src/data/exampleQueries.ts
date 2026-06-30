export interface ExampleQuery {
  category: string
  question: string
}

export const EXAMPLE_QUERIES: ExampleQuery[] = [
  {
    category: 'Platform Risk',
    question: 'What are the biggest threats to my Generative AI application?',
  },
  {
    category: 'Incident Analysis',
    question:
      'Show me how a real-world attack on a facial recognition system unfolded step by step.',
  },
  {
    category: 'Compliance Check',
    question:
      'Which of my current defenses satisfy EU AI Act requirements?',
  },
  {
    category: 'Gap Analysis',
    question:
      "Where are the blind spots in my AI system's security coverage?",
  },
]
