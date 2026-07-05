export interface HealthResponse {
  status: string;
  version: string;
}

export interface ConceptResponse {
  name: string;
  description: string;
  category: string;
}

export interface SearchResponse {
  results: ConceptResponse[];
}