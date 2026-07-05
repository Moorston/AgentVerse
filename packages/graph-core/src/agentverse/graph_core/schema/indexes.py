"""Neo4j index definitions."""

INDEXES: list[str] = [
    # Original 4 indexes
    "CREATE INDEX IF NOT EXISTS FOR (a:Agent) ON (a.name)",
    "CREATE INDEX IF NOT EXISTS FOR (f:Framework) ON (f.name)",
    "CREATE INDEX IF NOT EXISTS FOR (c:Concept) ON (c.name)",
    "CREATE INDEX IF NOT EXISTS FOR (p:Paper) ON (p.title)",
    # New 8 indexes (Phase 1-3)
    "CREATE INDEX IF NOT EXISTS FOR (n:News) ON (n.title)",
    "CREATE INDEX IF NOT EXISTS FOR (p:Product) ON (p.name)",
    "CREATE INDEX IF NOT EXISTS FOR (co:Company) ON (co.name)",
    "CREATE INDEX IF NOT EXISTS FOR (mt:MemoryType) ON (mt.name)",
    "CREATE INDEX IF NOT EXISTS FOR (mf:MemoryFramework) ON (mf.name)",
    "CREATE INDEX IF NOT EXISTS FOR (app:Application) ON (app.name)",
    "CREATE INDEX IF NOT EXISTS FOR (pat:Pattern) ON (pat.name)",
    "CREATE INDEX IF NOT EXISTS FOR (it:IndustryTrend) ON (it.name)",
    # Performance indexes
    "CREATE INDEX IF NOT EXISTS FOR (p:Paper) ON (p.published_date)",
    "CREATE INDEX IF NOT EXISTS FOR (f:Framework) ON (f.stars)",
]


async def apply_indexes(client) -> None:
    """Apply all Neo4j indexes."""
    async with client.session() as session:
        for cql in INDEXES:
            await session.run(cql)