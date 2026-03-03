# Week 12: Data Engineering for AI + Portfolio Project #2

**Month:** 3 (Intelligence) | **Duration:** 8-10 hours | **Priority:** 🟡 RECOMMENDED

---

## Overview

**Connection to previous weeks:** You've built agents and RAG systems — now it's time to understand where the data comes from. In enterprise, AI engineers work with data teams to access training data, manage embeddings, and ensure data quality. These skills are frequently tested in interviews.

AI systems are only as good as their data. This week covers **data engineering fundamentals** that AI engineers need: SQL, data pipelines, data quality, and feature stores. You'll also complete Portfolio Project #2.

---

## Prerequisites

- Basic SQL knowledge (SELECT, WHERE, JOIN) — if rusty, review [SQL basics](https://www.w3schools.com/sql/sql_intro.asp)
- Completed Weeks 1-11

---

## Learning Objectives

By the end of this week, you will:
- Write SQL queries for AI/ML data extraction
- Understand data pipeline patterns (ETL/ELT)
- Implement data quality checks
- Know about feature stores and embedding management
- Complete Portfolio Project #2 (AI Agent)

---

## Theory (2 hours)

### 1. SQL for AI Engineers (45 min)

**Why SQL matters for AI:**
- Extract training data
- Query vector databases (many use SQL-like syntax)
- Build analytics on AI usage
- Manage embeddings and metadata

**Essential SQL patterns:**

```sql
-- JOINs: Combine data from multiple tables
SELECT 
    d.document_id,
    d.content,
    e.embedding,
    c.chunk_index
FROM documents d
JOIN embeddings e ON d.document_id = e.document_id
JOIN chunks c ON e.chunk_id = c.chunk_id
WHERE d.created_at > '2024-01-01';

-- CTEs: Complex queries made readable
WITH recent_documents AS (
    SELECT * FROM documents
    WHERE created_at > NOW() - INTERVAL '30 days'
),
chunked AS (
    SELECT 
        rd.document_id,
        COUNT(*) as chunk_count
    FROM recent_documents rd
    JOIN chunks c ON rd.document_id = c.document_id
    GROUP BY rd.document_id
)
SELECT * FROM chunked WHERE chunk_count > 10;

-- Window functions: Analytics
SELECT 
    document_id,
    chunk_text,
    similarity_score,
    ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY similarity_score DESC) as rank
FROM search_results
WHERE query_id = 123;
```

**Interview tip:** Be comfortable with JOINs, CTEs, GROUP BY, and window functions (ROW_NUMBER, RANK).

### 2. Data Pipelines (30 min)

**ETL vs ELT:**
| Pattern | Process | Best For |
|---------|---------|----------|
| **ETL** | Extract → Transform → Load | On-premise, limited storage |
| **ELT** | Extract → Load → Transform | Cloud, data lakes |

**AI-specific pipeline stages:**
```
Raw Documents → [Ingestion] → [Cleaning] → [Chunking] → [Embedding] → Vector DB
                     ↓            ↓            ↓             ↓
                   Store       Validate    Metadata      Index
```

**Pipeline orchestration tools:**
| Tool | Type | Use Case |
|------|------|----------|
| **Airflow** | Open source | Complex DAGs, scheduling |
| **Prefect** | Modern Python | Simpler than Airflow |
| **dbt** | SQL transforms | Data modeling |
| **Azure Data Factory** | Cloud | Enterprise ETL |

### 3. Data Quality (30 min)

**Data quality dimensions:**
- **Completeness** — No missing values
- **Accuracy** — Values are correct
- **Consistency** — Same format everywhere
- **Timeliness** — Data is current
- **Validity** — Values within expected range

**Implementing quality checks:**

```python
# Great Expectations style
expectations = [
    {"column": "text", "expectation": "not_null"},
    {"column": "embedding", "expectation": "length_equals", "value": 1536},
    {"column": "created_at", "expectation": "date_not_in_future"},
]

def validate_row(row: dict, expectations: list) -> list:
    failures = []
    for exp in expectations:
        if exp["expectation"] == "not_null":
            if row.get(exp["column"]) is None:
                failures.append(f"{exp['column']} is null")
        elif exp["expectation"] == "length_equals":
            if len(row.get(exp["column"], [])) != exp["value"]:
                failures.append(f"{exp['column']} wrong length")
    return failures
```

**Quality gates:**
- Block ingestion if quality < threshold
- Alert on quality degradation
- Track quality metrics over time

### 4. Feature Stores & Embedding Management (30 min)

**What is a feature store?**
A centralized repository for ML features — reusable, versioned, production-ready.

```
Raw Data → [Feature Pipeline] → Feature Store → ML Training
                                      ↓
                               Online Serving
```

**Key concepts:**
| Concept | Description |
|---------|-------------|
| **Feature** | A measurable input variable |
| **Entity** | The key (user_id, document_id) |
| **Offline store** | Historical features for training |
| **Online store** | Low-latency serving |

**Embedding management patterns:**

```python
# Embedding storage schema
embeddings_table = """
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    entity_type VARCHAR(50),       -- 'document', 'chunk', 'user'
    entity_id VARCHAR(255),
    model_name VARCHAR(100),       -- 'text-embedding-3-small'
    model_version VARCHAR(50),
    embedding VECTOR(1536),
    created_at TIMESTAMP,
    metadata JSONB
);

CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);
"""

# Track embedding versions
def store_embedding(entity_id: str, embedding: list, model: str):
    return {
        "entity_id": entity_id,
        "embedding": embedding,
        "model_name": model,
        "model_version": "2024-01",
        "created_at": datetime.now()
    }
```

---

## Hands-On Practice (4-6 hours)

### Task 1: SQL for RAG Data (45 min)

```python
# sql_for_rag.py
import sqlite3
from datetime import datetime

# Create a sample database
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# Create tables
cursor.executescript("""
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename TEXT,
    content TEXT,
    created_at TIMESTAMP
);

CREATE TABLE chunks (
    id INTEGER PRIMARY KEY,
    document_id INTEGER,
    chunk_index INTEGER,
    chunk_text TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

CREATE TABLE search_logs (
    id INTEGER PRIMARY KEY,
    query TEXT,
    top_result_id INTEGER,
    similarity_score REAL,
    timestamp TIMESTAMP
);
""")

# Insert sample data
cursor.executemany(
    "INSERT INTO documents (filename, content, created_at) VALUES (?, ?, ?)",
    [
        ("policy.txt", "Vacation policy content...", "2024-01-15"),
        ("benefits.txt", "Benefits information...", "2024-01-20"),
        ("remote.txt", "Remote work guidelines...", "2024-02-01"),
    ]
)

cursor.executemany(
    "INSERT INTO chunks (document_id, chunk_index, chunk_text) VALUES (?, ?, ?)",
    [
        (1, 0, "Employees receive 20 days PTO"),
        (1, 1, "Request vacation 2 weeks ahead"),
        (2, 0, "401k matching up to 4%"),
        (3, 0, "Remote work on Tuesdays and Thursdays"),
    ]
)

cursor.executemany(
    "INSERT INTO search_logs (query, top_result_id, similarity_score, timestamp) VALUES (?, ?, ?, ?)",
    [
        ("vacation days", 1, 0.92, "2024-03-01 10:00:00"),
        ("401k", 3, 0.88, "2024-03-01 10:05:00"),
        ("remote work", 4, 0.95, "2024-03-01 10:10:00"),
        ("vacation policy", 1, 0.94, "2024-03-01 11:00:00"),
    ]
)
conn.commit()

# Practice queries
print("=== Query 1: Documents with chunk counts ===")
cursor.execute("""
    SELECT d.filename, COUNT(c.id) as chunk_count
    FROM documents d
    LEFT JOIN chunks c ON d.id = c.document_id
    GROUP BY d.id
    ORDER BY chunk_count DESC
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} chunks")

print("\n=== Query 2: Most searched documents ===")
cursor.execute("""
    WITH search_counts AS (
        SELECT 
            top_result_id,
            COUNT(*) as search_count,
            AVG(similarity_score) as avg_score
        FROM search_logs
        GROUP BY top_result_id
    )
    SELECT 
        c.chunk_text,
        sc.search_count,
        ROUND(sc.avg_score, 2) as avg_score
    FROM search_counts sc
    JOIN chunks c ON sc.top_result_id = c.id
    ORDER BY sc.search_count DESC
""")
for row in cursor.fetchall():
    print(f"  {row[0][:40]}... (searches: {row[1]}, avg score: {row[2]})")

print("\n=== Query 3: Search quality over time ===")
cursor.execute("""
    SELECT 
        date(timestamp) as day,
        COUNT(*) as queries,
        ROUND(AVG(similarity_score), 3) as avg_similarity
    FROM search_logs
    GROUP BY date(timestamp)
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} queries, avg similarity: {row[2]}")

conn.close()
```

### Task 2: Data Pipeline for Documents (60 min)

```python
# document_pipeline.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import hashlib
import json

@dataclass
class PipelineStage:
    name: str
    started_at: datetime = None
    completed_at: datetime = None
    records_in: int = 0
    records_out: int = 0
    errors: List[str] = None

@dataclass
class Document:
    id: str
    filename: str
    content: str
    metadata: dict

class DocumentPipeline:
    """ETL pipeline for document processing."""
    
    def __init__(self):
        self.stages: List[PipelineStage] = []
    
    def _hash_content(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def extract(self, folder: str) -> List[Document]:
        """Extract: Load documents from folder."""
        stage = PipelineStage(name="extract", started_at=datetime.now(), errors=[])
        documents = []
        
        folder_path = Path(folder)
        for file in folder_path.glob("*.txt"):
            try:
                content = file.read_text()
                doc = Document(
                    id=self._hash_content(content),
                    filename=file.name,
                    content=content,
                    metadata={"path": str(file), "size": len(content)}
                )
                documents.append(doc)
            except Exception as e:
                stage.errors.append(f"Error reading {file}: {e}")
        
        stage.records_out = len(documents)
        stage.completed_at = datetime.now()
        self.stages.append(stage)
        
        return documents
    
    def transform(self, documents: List[Document]) -> List[Document]:
        """Transform: Clean and validate documents."""
        stage = PipelineStage(
            name="transform", 
            started_at=datetime.now(), 
            records_in=len(documents),
            errors=[]
        )
        
        cleaned = []
        for doc in documents:
            # Basic cleaning
            content = doc.content.strip()
            content = ' '.join(content.split())  # Normalize whitespace
            
            # Validation
            if len(content) < 10:
                stage.errors.append(f"{doc.filename}: Too short")
                continue
            
            doc.content = content
            doc.metadata["word_count"] = len(content.split())
            cleaned.append(doc)
        
        stage.records_out = len(cleaned)
        stage.completed_at = datetime.now()
        self.stages.append(stage)
        
        return cleaned
    
    def load(self, documents: List[Document], output_path: str) -> int:
        """Load: Save processed documents."""
        stage = PipelineStage(
            name="load",
            started_at=datetime.now(),
            records_in=len(documents),
            errors=[]
        )
        
        output = Path(output_path)
        output.mkdir(exist_ok=True)
        
        saved = 0
        for doc in documents:
            try:
                doc_file = output / f"{doc.id}.json"
                with open(doc_file, "w") as f:
                    json.dump({
                        "id": doc.id,
                        "filename": doc.filename,
                        "content": doc.content,
                        "metadata": doc.metadata
                    }, f, indent=2)
                saved += 1
            except Exception as e:
                stage.errors.append(f"Error saving {doc.id}: {e}")
        
        stage.records_out = saved
        stage.completed_at = datetime.now()
        self.stages.append(stage)
        
        return saved
    
    def run(self, input_folder: str, output_folder: str) -> dict:
        """Run the full ETL pipeline."""
        print("Starting document pipeline...")
        
        # E
        docs = self.extract(input_folder)
        print(f"  Extracted: {len(docs)} documents")
        
        # T
        docs = self.transform(docs)
        print(f"  Transformed: {len(docs)} documents")
        
        # L
        saved = self.load(docs, output_folder)
        print(f"  Loaded: {saved} documents")
        
        return self.summary()
    
    def summary(self) -> dict:
        """Get pipeline run summary."""
        total_errors = sum(len(s.errors or []) for s in self.stages)
        return {
            "stages": len(self.stages),
            "total_errors": total_errors,
            "stages_detail": [
                {
                    "name": s.name,
                    "records_in": s.records_in,
                    "records_out": s.records_out,
                    "duration_ms": (s.completed_at - s.started_at).total_seconds() * 1000,
                    "errors": len(s.errors or [])
                }
                for s in self.stages
            ]
        }

# Usage
if __name__ == "__main__":
    pipeline = DocumentPipeline()
    # summary = pipeline.run("docs/", "processed/")
    # print(json.dumps(summary, indent=2))
    print("Pipeline ready. Call pipeline.run('input/', 'output/')")
```

### Task 3: Data Quality Checks (45 min)

```python
# data_quality.py
from dataclasses import dataclass
from typing import List, Dict, Any, Callable
from datetime import datetime
import json

@dataclass
class QualityRule:
    name: str
    column: str
    check: Callable[[Any], bool]
    severity: str = "error"  # "error" or "warning"

@dataclass
class QualityResult:
    rule_name: str
    passed: bool
    failed_count: int
    sample_failures: List[str]

class DataQualityChecker:
    """Check data quality for AI datasets."""
    
    def __init__(self):
        self.rules: List[QualityRule] = []
    
    def add_rule(self, name: str, column: str, check: Callable, severity: str = "error"):
        self.rules.append(QualityRule(name, column, check, severity))
    
    def check(self, data: List[Dict]) -> Dict:
        """Run all quality checks on data."""
        results = []
        
        for rule in self.rules:
            failures = []
            for i, row in enumerate(data):
                value = row.get(rule.column)
                if not rule.check(value):
                    failures.append(f"Row {i}: {rule.column}={value}")
            
            results.append(QualityResult(
                rule_name=rule.name,
                passed=len(failures) == 0,
                failed_count=len(failures),
                sample_failures=failures[:3]
            ))
        
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_rules": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 1.0,
            "results": [
                {
                    "rule": r.rule_name,
                    "passed": r.passed,
                    "failed_count": r.failed_count,
                    "samples": r.sample_failures
                }
                for r in results
            ]
        }

# Create checker for RAG data
def create_rag_quality_checker() -> DataQualityChecker:
    checker = DataQualityChecker()
    
    # Text quality
    checker.add_rule(
        "text_not_empty",
        "text",
        lambda x: x is not None and len(str(x).strip()) > 0
    )
    checker.add_rule(
        "text_min_length",
        "text",
        lambda x: len(str(x)) >= 50 if x else False
    )
    
    # Embedding quality
    checker.add_rule(
        "embedding_exists",
        "embedding",
        lambda x: x is not None
    )
    checker.add_rule(
        "embedding_dimension",
        "embedding",
        lambda x: len(x) == 1536 if x else False
    )
    checker.add_rule(
        "embedding_normalized",
        "embedding",
        lambda x: abs(sum(v**2 for v in x) - 1.0) < 0.01 if x else False
    )
    
    # Metadata quality
    checker.add_rule(
        "source_exists",
        "source",
        lambda x: x is not None and len(str(x)) > 0
    )
    
    return checker

# Test
if __name__ == "__main__":
    checker = create_rag_quality_checker()
    
    # Sample data
    test_data = [
        {"text": "This is a valid chunk of text with enough content.", 
         "embedding": [0.1] * 1536, "source": "doc1.txt"},
        {"text": "", "embedding": None, "source": ""},  # Bad row
        {"text": "Another valid text chunk here with sufficient length.", 
         "embedding": [0.2] * 1536, "source": "doc2.txt"},
        {"text": "Short", "embedding": [0.1] * 100, "source": "doc3.txt"},  # Wrong dim
    ]
    
    results = checker.check(test_data)
    print(json.dumps(results, indent=2))
```

### Task 4: Embedding Version Management (45 min)

```python
# embedding_manager.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
import json

@dataclass
class EmbeddingRecord:
    entity_id: str
    entity_type: str
    embedding: List[float]
    model_name: str
    model_version: str
    created_at: datetime
    metadata: Dict = None

class EmbeddingManager:
    """Manage embedding versions and updates."""
    
    def __init__(self):
        self.store: Dict[str, List[EmbeddingRecord]] = {}  # entity_id -> versions
        self.current_model = "text-embedding-3-small"
        self.current_version = "2024-01"
    
    def store_embedding(
        self,
        entity_id: str,
        entity_type: str,
        embedding: List[float],
        metadata: Dict = None
    ) -> EmbeddingRecord:
        """Store a new embedding."""
        record = EmbeddingRecord(
            entity_id=entity_id,
            entity_type=entity_type,
            embedding=embedding,
            model_name=self.current_model,
            model_version=self.current_version,
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        if entity_id not in self.store:
            self.store[entity_id] = []
        self.store[entity_id].append(record)
        
        return record
    
    def get_latest(self, entity_id: str) -> Optional[EmbeddingRecord]:
        """Get the most recent embedding for an entity."""
        versions = self.store.get(entity_id, [])
        if not versions:
            return None
        return max(versions, key=lambda x: x.created_at)
    
    def get_by_version(self, entity_id: str, model_version: str) -> Optional[EmbeddingRecord]:
        """Get embedding for a specific model version."""
        versions = self.store.get(entity_id, [])
        for v in versions:
            if v.model_version == model_version:
                return v
        return None
    
    def needs_update(self, entity_id: str) -> bool:
        """Check if entity needs re-embedding with current model."""
        latest = self.get_latest(entity_id)
        if not latest:
            return True
        return latest.model_version != self.current_version
    
    def get_outdated(self) -> List[str]:
        """Get all entities that need re-embedding."""
        outdated = []
        for entity_id in self.store:
            if self.needs_update(entity_id):
                outdated.append(entity_id)
        return outdated
    
    def update_model_version(self, new_version: str):
        """Update the current model version (triggers re-embedding)."""
        self.current_version = new_version
        outdated = self.get_outdated()
        print(f"Model updated to {new_version}. {len(outdated)} entities need re-embedding.")
        return outdated

# Test
if __name__ == "__main__":
    manager = EmbeddingManager()
    
    # Store some embeddings
    manager.store_embedding("doc_001", "document", [0.1] * 1536)
    manager.store_embedding("doc_002", "document", [0.2] * 1536)
    
    print(f"Latest for doc_001: {manager.get_latest('doc_001').model_version}")
    print(f"Needs update: {manager.needs_update('doc_001')}")
    
    # Simulate model update
    print("\n--- Updating model version ---")
    outdated = manager.update_model_version("2024-02")
    print(f"Outdated entities: {outdated}")
```

---

## Portfolio Project #2: AI Agent

This week you complete Portfolio Project #2. See [projects/02_ai_agent/README.md](../projects/02_ai_agent/README.md) for full requirements.

**Key requirements:**
- Tool definitions (3+ tools)
- ReAct-style reasoning
- Error handling
- Logging of agent steps

---

## Knowledge Checklist

- [ ] I can write JOINs, CTEs, and window functions in SQL
- [ ] I understand ETL vs ELT pipeline patterns
- [ ] I can implement data quality checks
- [ ] I understand feature stores and embedding management
- [ ] I can track embedding versions for model updates
- [ ] I completed Portfolio Project #2

---

## Deliverables

1. `sql_for_rag.py` — SQL query practice
2. `document_pipeline.py` — ETL pipeline
3. `data_quality.py` — Quality checking
4. `embedding_manager.py` — Version management

---

## What's Next?

Next week: **Observability & Monitoring** for production AI systems!

---

## Resources

- [SQL Tutorial](https://www.sqltutorial.org/)
- [Great Expectations](https://greatexpectations.io/)
- [Feature Store Concepts](https://www.featurestore.org/)
- [Apache Airflow](https://airflow.apache.org/)
