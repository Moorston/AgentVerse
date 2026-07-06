"""Extraction prompt templates."""

PAPER_EXTRACTION_PROMPT = """Extract the following from the paper text:
- Title
- Authors
- Abstract
- Key concepts mentioned (PascalCase names only, with category)
- Related frameworks (PascalCase names only)
- Contribution type (method, survey, benchmark, analysis, system)

Rules:
- Concept names MUST be PascalCase (e.g., ChainOfThought, not chain-of-thought)
- Do NOT include generic terms (LLMs, AI, models, data)
- Categories: reasoning, planning, memory, tool_use, reflection, multi_agent, workflow, protocol, rag, prompt_engineering

Text: {text}
"""

CONCEPT_EXTRACTION_PROMPT = """Identify and extract AI Agent concepts from the text.
For each concept provide: name (PascalCase), description, and category.

Rules:
- ALL names MUST be PascalCase (e.g., ChainOfThought, not chain-of-thought)
- Do NOT extract generic terms: LLMs, AI, models, data, safety, performance
- ONLY extract specific techniques, methods, frameworks, architectures

Text: {text}
"""

RELATIONSHIP_EXTRACTION_PROMPT = """Extract relationships between AI Agent concepts.

Rules:
- source = the method/framework/technique that acts or proposes
- target = the entity being affected, extended, or supported
- Example: ReAct EXTENDS ChainOfThought (ReAct is source, ChainOfThought is target)
- Use PascalCase for concept names
- Do NOT create relationships involving generic terms (LLMs, AI, models)

Text: {text}
"""