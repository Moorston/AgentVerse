"""Neo4j uniqueness constraints."""

CONSTRAINTS: list[str] = [
    # Original 5 labels
    "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Agent) REQUIRE a.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Framework) REQUIRE f.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Paper) REQUIRE p.doi IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (pr:Protocol) REQUIRE pr.name IS UNIQUE",
    # New 8 labels (Phase 1-3)
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:News) REQUIRE n.url IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (co:Company) REQUIRE co.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (mt:MemoryType) REQUIRE mt.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (mf:MemoryFramework) REQUIRE mf.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (app:Application) REQUIRE app.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (pat:Pattern) REQUIRE pat.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (it:IndustryTrend) REQUIRE it.name IS UNIQUE",
]


async def apply_constraints(client) -> None:
    """Apply all Neo4j constraints."""
    async with client.session() as session:
        for cql in CONSTRAINTS:
            await session.run(cql)