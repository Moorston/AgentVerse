"""Tests for graph-core models."""

from agentverse.graph_core.models.node import GraphNode, GraphRelationship
from agentverse.graph_core.models.query import Query
from agentverse.graph_core.models.relationship import RelationshipType


def test_graph_node_defaults():
    """GraphNode should have empty defaults."""
    node = GraphNode()
    assert node.labels == []
    assert node.properties == {}
    assert node.element_id is None


def test_graph_node_with_data():
    """GraphNode should accept labels and properties."""
    node = GraphNode(labels=["Concept"], properties={"name": "ReAct"})
    assert node.labels == ["Concept"]
    assert node.properties["name"] == "ReAct"


def test_graph_relationship():
    """GraphRelationship should store type and properties."""
    rel = GraphRelationship(type="PROPOSES", properties={"weight": 0.9})
    assert rel.type == "PROPOSES"
    assert rel.properties["weight"] == 0.9


def test_query_defaults():
    """Query should have empty params by default."""
    q = Query(statement="MATCH (n) RETURN n")
    assert q.statement == "MATCH (n) RETURN n"
    assert q.parameters == {}


def test_relationship_types():
    """RelationshipType enum should have all expected values."""
    assert RelationshipType.PROPOSES == "PROPOSES"
    assert RelationshipType.IMPLEMENTS == "IMPLEMENTS"
    assert RelationshipType.EVOLVES_TO == "EVOLVES_TO"
    assert RelationshipType.RELATED_TO == "RELATED_TO"
    assert RelationshipType.CITES == "CITES"
    assert RelationshipType.IMPLEMENTS_MEMORY == "IMPLEMENTS_MEMORY"
