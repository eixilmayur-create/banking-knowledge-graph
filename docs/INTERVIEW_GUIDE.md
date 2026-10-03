# Interview guide

## 60-second introduction

“I built a banking knowledge graph prototype to connect fragmented customer and product records. The pipeline cleans synthetic data, explores identity resolution, models banking semantics in RDF, checks constraints with SHACL, and prepares a Neo4j graph. A FastAPI and Streamlit application exposes Customer 360 and GraphRAG. Gemini routes questions to a controlled query catalog, then generates answers from retrieved evidence. The key design choice is separating semantic validation from operational graph retrieval, while keeping the system's limitations explicit.”

## Five-minute walkthrough

1. **Problem:** Different source systems represent the same customer inconsistently.
2. **Data:** Explain normalization, matching signals and why false merges matter.
3. **Semantics:** Show an ontology class, a SHACL constraint and a SPARQL check.
4. **Retrieval:** Trace a customer → account → transaction traversal.
5. **Answer:** Show question, selected intent, returned evidence and answer together.
6. **Reflection:** Identify missing access controls, evaluation and production orchestration.

## Questions to prepare

| Question | Evidence-based answer |
| --- | --- |
| Why graphs instead of only SQL? | Connected-product and multi-hop questions map naturally to traversals; SQL remains a reasonable baseline and graph performance must be measured. |
| Why RDF and Neo4j? | RDF provides portable semantics and shape validation; Neo4j supports application traversals. Two representations add consistency overhead. |
| How do you avoid false entity merges? | Weighted signals and a review band illustrate the approach; threshold calibration and a completed review-to-merge workflow remain necessary. |
| Is this vector RAG? | The answer path uses intent-routed graph retrieval. Embeddings support separate schema-mapping experiments. |
| Does it prevent hallucinations? | Evidence-only prompts and insufficient-evidence responses reduce risk; faithfulness still requires evaluation. |
| Can the model execute arbitrary queries? | The retriever uses a predefined Cypher catalog with parameters. Authorization remains a separate requirement. |
| How would you scale it? | Profile query fan-out, batch imports, introduce orchestration and versioning, and benchmark realistic workloads before claiming scale. |
| What did you measure? | Cite only checks recorded in VALIDATION.md. Do not invent accuracy, throughput, cloud reliability or business impact. |

## Demo fallback

When cloud access is unavailable, show the offline pipeline, graph artifacts, SHACL report, query catalog and architecture. Clearly label this as an offline walkthrough; do not present simulated API responses as a live result.
