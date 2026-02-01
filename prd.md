y
# Product Requirement Document (PRD): Hybrid Graph-RAG System

## **Objective**

Build a documentation analysis system using a **Polyglot Architecture** (Python Backend / Node.js Frontend). The system will ingest HTML documentation, convert it to a traversable Knowledge Graph (Neo4j) with embedded text chunks, and serve a chat interface where answers are grounded in both **vector search** (finding the right section) and **graph connectivity** (finding related concepts).

**Environment Context:**

* **App Container:** Python 3.11, Node 20.
* **Database:** Neo4j 5 Community (`db:7687`).
* **LLM:** Ollama with Llama 3 (`ollama:11434`), running on host GPU.
* **Ports:** Host ports shifted (9xxx/11xxx) to prevent conflicts.

---

## **Phase 1: Project Initialization & Schema**
cc
Here is the updated **US-002** section, reflecting the move from strict, exhaustive lists to broad, flexible Enums for the CMS domain.

### **US-002: Define Schema Constants & API Models**

**Description:** Create a central configuration file (`schemas.py`) to define the "Source of Truth" for Graph Extraction. Instead of exhaustively listing every possible software term, use broad **Enum Categories** to guide the LLM.
**Tasks:**

1. **Create `backend/app/schemas.py**`:
2. **Define `EntityType` Enum:**
* *Software Parts:* `COMPONENT`, `MODULE`, `API`, `DATABASE_OBJECT`.
* *Logic:* `CONFIGURATION`, `WORKFLOW`, `EVENT`.
* *People:* `ROLE`.
* *Catch-All:* `CONCEPT` (Critical for abstract terms like "SEO" or "Versioning").


3. **Define `RelationType` Enum:**
* *Structure:* `CONTAINS`, `HAS_PART`.
* *Dependencies:* `DEPENDS_ON`, `EXTENDS`, `IMPLEMENTS`.
* *Logic:* `TRIGGERS`, `MAPPED_TO`, `STORES`.
* *Access:* `CAN_ACCESS`, `MANAGES`.
* *System:* `MENTIONED_IN` (Entity -> Chunk link).


4. **Define API Models:** Create `ChatResponse` (answer, sources) for the Frontend contract.

**Acceptance Criteria:**

* [ ] `schemas.py` exists and contains `EntityType` and `RelationType` Enums.
* [ ] The `Concept` type is included to catch abstract entities.
* [ ] API Response model includes a `sources` list.

**Quality Gates:**

* `python -c "from app.schemas import EntityType; print(EntityType.CONCEPT.value)"` prints "Concept".

---

## **Phase 2: Backend Ingestion Pipeline (Python)**

### **US-003: HTML to Semantic Markdown Conversion**

**Description:** Implement cleaning module using `markdownify`.
**Tasks:**

1. Implement `clean_and_convert(html: str) -> str`.
2. Strip `<nav>`, `<footer>`, `<script>`.
3. Convert HTML tables to Markdown pipes `|` (preserving data structure).
**Quality Gates:**

* `pytest tests/test_converter.py` -> Output contains Markdown table syntax.

### **US-004: Header-Based Chunking & Embedding**

**Description:** Split text by headers, inject metadata, and generate vector embeddings for the text chunks.
**Tasks:**

1. **Split:** Use `MarkdownHeaderTextSplitter` (H1, H2, H3).
2. **Metadata:** Inject context (`{'h1': 'Title', 'h2': 'Section'}`) and prepend "Breadcrumb" string to chunk text.
3. **Embed:** Initialize `OllamaEmbeddings` with `nomic-embed-text`.
```python
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://ollama:11434"
)

```



**Quality Gates:**

* `pytest tests/test_chunking.py` -> Assert chunk metadata matches input headers and embedding object initializes correctly.

### **US-005: Extraction & Immediate Persistence**

**Description:** Process chunks one by one, extract entities, link them to the source chunk, and persist to Neo4j.
**Tasks:**

1. **Extract:** Use `LLMGraphTransformer` to convert text chunk -> Graph Documents.
2. **Normalize:** Title Case/Lowercase Node IDs to prevent duplicates (e.g., "field editor" -> "Field Editor").
3. **Save:** Call `neo4j_graph.add_graph_documents([doc])` immediately.
4. **Link:** Ensure the pipeline creates the `:MENTIONED_IN` relationship between the Entity and the Source Chunk (which holds the text vector).
**Acceptance Criteria:**

Prune (The Safety Valve): Before saving, check the extracted Entity IDs against a Stop List.

STOP_LIST = ["System", "Application", "User", "Administrator", "Platform", "Data", "Feature"]

Action: If an ID is in this list, discard it. Do not create the node.

Why: These terms are too generic; connecting to them destroys the value of the graph.

* [ ] Graph grows incrementally as script runs.
* [ ] "Field Editor" appears as 1 node, even if mentioned in 50 chunks.
* [ ] Vector Index exists on the `Chunk` nodes.

---

## **Phase 3: Backend API (Python/FastAPI)**

### **US-007: Graph-Enhanced Hybrid Retrieval Strategy**

**Description:** Implement the sophisticated retrieval logic that uses the Graph for "Reasoning" (finding connections) and the Vector Store for "Evidence" (getting the text).
**Tasks:**

Step A: Entity Extraction (The "Search Terms")

Implement a lightweight LLM call to parse the User Query.

Input: "How does the system map fields to the database?"

Output: ["Field", "Database", "Map"].

Step B: Graph Traversal (The "Reasoning" Layer)

Node Lookup: Search the Neo4j graph for nodes matching the extracted entities (fuzzy match).

Expansion: For every hit (e.g., "Field"), traverse 1 hop to find connected neighbors.

Discovery: Finds edge (Field) --[MAPPED_TO]--> (Database Column).

Node Collection: Collect ALL unique nodes found in this step (Original Hits + Neighbors).

Step C: Universal Source Retrieval (The "Evidence" Layer)

Vector Hits: Perform standard Vector Search to get top 3 relevant chunks.

Graph Hits: For every Node found in Step B, traverse back to its source: (:Entity)-[:MENTIONED_IN]->(:Chunk).

"Traverse the :MENTIONED_IN relationship backwards. If an entity is linked to more than 3 chunks, use Vector Similarity (Chunk Vector vs User Query) to select the top 3 most relevant chunks. Retrieve the full text for these selected chunks."

Aggregation: Combine the "Vector Chunks" and "Graph Chunks" into one unique list.

Fetch: Retrieve the text property for all of these chunks.

Why: If the graph says "Field" relates to "Database Column", we must provide the LLM with the full documentation section about "Database Column" so it has the context to explain the connection.


**Step D: Context Assembly & Generation**

1. Construct the Final System Prompt with two distinct sections:
* `--- GRAPH KNOWLEDGE ---`: The high-level relationships found in Step B.
* `--- SOURCE DOCUMENTS ---`: The raw text chunks fetched in Step C.


2. Send to LLM (Ollama/Llama 3) for the final answer.

**Acceptance Criteria:**

* [ ] **Reasoning Test:** If User asks about "Field Editor", the system includes context about "Data Types" (because they are connected neighbors).
* [ ] **Traceability:** The API response includes a `sources` array listing the chunks used.
**Quality Gates:**
* `curl -X POST /chat` with a complex query returns a detailed answer.

---

## **Phase 4: Frontend UI (Node.js)**

### **US-008: Next.js Chat Interface**

**Description:** Build the chat UI.
**Tasks:**

1. Configure Next.js to run on port 3030.
2. Create Chat Component (Input + Message List).
3. Render Markdown responses using `react-markdown`.
4. Connect to FastAPI endpoint.
**Quality Gates:**

* `npm run dev` -> Accessible at `http://localhost:3030`.

### **US-009: Frontend Integration & Visualization**

**Description:** Update the chat interface to display the retrieval process transparency.
**Tasks:**

1. Parse the API response to separate the "Answer" from the "Sources".
2. Display the "Answer" in the main chat bubble.
3. Display a "Reasoning" collapsible section showing:
* "Found Entities: Field, Database"
* "Used Graph Connections: Field -> Database Column"
**Acceptance Criteria:**



* [ ] UI shows the final answer clearly.
* [ ] UI indicates which sources were used.