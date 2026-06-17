// Q1 — Generative AI threats with deployment-time mitigations
// "Which techniques target Generative AI and which mitigations
//  apply at deployment time, owned by which lifecycle phase?"
MATCH (t:Technique)
WHERE 'Generative AI' IN t.platforms
MATCH (t)<-[:MITIGATES]-(m:Mitigation)
WHERE 'Deployment' IN m.lifecycle_phases
MATCH (t)-[:ACHIEVES]->(tac:Tactic)
RETURN tac.name AS tactic, t.id, t.name AS technique,
       m.id, m.name AS mitigation, m.categories
ORDER BY tac.name, t.name;

// Q2 — Coverage gap analysis
// "Which techniques have NO mitigations? (gaps in ATLAS coverage)"
MATCH (t:Technique)
WHERE NOT (t)<-[:MITIGATES]-()
  AND NOT t.is_subtechnique
RETURN t.id, t.name, t.platforms, t.maturity
ORDER BY t.maturity, t.name;

// Q3 — Attack chain traversal
// "Show the full ordered attack chain for a specific case study"
MATCH (cs:CaseStudy {id: 'AML.CS0012'})
MATCH (s:AttackStep)-[:STEP_OF]->(cs)
MATCH (s)-[:USES]->(t:Technique)
MATCH (s)-[:IN_TACTIC]->(tac:Tactic)
OPTIONAL MATCH (s)-[:LEADS_TO]->(next:AttackStep)
RETURN s.step_id, tac.name AS tactic, t.name AS technique, s.description,
       next.step_id AS next_step
ORDER BY s.step_id;

// Q4 — Most exploited techniques across all case studies
// "Which techniques appear in the most real-world incidents?"
MATCH (s:AttackStep)-[:USES]->(t:Technique)
MATCH (s)-[:STEP_OF]->(cs:CaseStudy)
RETURN t.id, t.name, t.platforms,
       count(DISTINCT cs) AS case_study_count,
       collect(DISTINCT cs.name)[..3] AS example_cases
ORDER BY case_study_count DESC
LIMIT 15;

// Q5 — Policy vs Technical mitigation split
// "For each tactic, how many technical vs policy mitigations exist?"
MATCH (tac:Tactic)<-[:ACHIEVES]-(t:Technique)<-[:MITIGATES]-(m:Mitigation)
RETURN tac.name AS tactic,
       sum(CASE WHEN 'Policy' IN m.categories THEN 1 ELSE 0 END) AS policy_count,
       sum(CASE WHEN 'Technical - AI' IN m.categories THEN 1 ELSE 0 END) AS technical_ai_count,
       sum(CASE WHEN 'Technical - Cyber' IN m.categories THEN 1 ELSE 0 END) AS technical_cyber_count
ORDER BY tac.name;

// Q6 — Cross-layer: ATLAS techniques to OWASP risks for Agentic AI
// "For Agentic AI techniques, what OWASP risks do they map to?"
// (Requires Phase 3 bridge nodes — returns empty until bridges are loaded)
MATCH (t:Technique)
WHERE 'Agentic AI' IN t.platforms
MATCH (t)-[:MAPS_TO]->(o:OWASPRisk)
MATCH (t)<-[:MITIGATES]-(m:Mitigation)
RETURN o.id, o.name AS owasp_risk,
       collect(DISTINCT t.name)[..5] AS techniques,
       collect(DISTINCT m.name)[..3] AS sample_mitigations
ORDER BY o.id;

// Q7 — The full cross-layer killer query
// "For a Generative AI system: threats, OWASP mapping,
//  deployment mitigations, regulatory coverage"
// (Requires Phase 3 bridge nodes — returns empty until bridges are loaded)
MATCH (t:Technique)
WHERE 'Generative AI' IN t.platforms
MATCH (t)-[:ACHIEVES]->(tac:Tactic)
OPTIONAL MATCH (t)-[:MAPS_TO]->(o:OWASPRisk)
MATCH (t)<-[:MITIGATES]-(m:Mitigation)
WHERE 'Deployment' IN m.lifecycle_phases
OPTIONAL MATCH (m)-[:SATISFIES]->(a:RegulatoryArticle)
RETURN tac.name AS tactic,
       t.id, t.name AS technique,
       o.name AS owasp_risk,
       m.name AS mitigation,
       m.categories AS mit_category,
       collect(DISTINCT a.id) AS regulatory_articles
ORDER BY tac.name, t.name;

// Q8 — Cross-layer: ATLAS mitigations to EU AI Act compliance
// "Which mitigations satisfy Article 15 and what techniques do they cover?"
// (Requires Phase 3 bridge nodes — returns empty until bridges are loaded)
MATCH (a:RegulatoryArticle {id: 'EU_AIA_Art15'})
MATCH (m:Mitigation)-[:SATISFIES]->(a)
MATCH (m)-[:MITIGATES]->(t:Technique)
RETURN m.id, m.name AS mitigation,
       m.lifecycle_phases,
       collect(t.name) AS techniques_covered
ORDER BY m.name;
