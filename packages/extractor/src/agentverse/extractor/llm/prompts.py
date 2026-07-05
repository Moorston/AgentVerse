"""Extraction prompt templates."""

PAPER_EXTRACTION_PROMPT = """Extract the following from the paper text:
- Title
- Authors
- Abstract
- Key concepts mentioned
- Related frameworks
- Contribution type (method, survey, benchmark, etc.)

Text: {text}
"""

CONCEPT_EXTRACTION_PROMPT = """Identify and extract AI Agent concepts from the text.
For each concept provide: name, description, category, and related terms.

Text: {text}
"""

RELATIONSHIP_EXTRACTION_PROMPT = """Extract relationships between AI Agent concepts.
For each relationship provide: source, target, relationship type, and evidence.

Text: {text}
"""