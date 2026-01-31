# Product Requirement Document (PRD): Hybrid Graph-RAG System

## **Objective**

Build a documentation analysis system using a **Polyglot Architecture** (Python Backend / Node.js Frontend). The system will ingest HTML documentation, convert it to a traversable Knowledge Graph (Neo4j), and serve a chat interface where answers are grounded in both vector search and graph connectivity.

**Environment Context:** * **App Container:** Python 3.11, Node 20.

* **Database:** Neo4j 5 Enterprise (`db:7687`).
* **LLM:** Ollama with Llama 3 (`ollama:11434`), running on host GPU.
* **Ports:** Host ports shifted (9xxx/11xxx) to prevent conflicts.

---

## **Phase 1: Project Initialization & Schema**

### **US-001: Workspace Initialization**

**Description:** Configure the Dev Container environment to bootstrap the project automatically.
**Tasks:**
Create backend/pyproject.toml (Poetry) with dependencies:

Core API: fastapi, uvicorn, python-multipart.

Graph & Data: neo4j, networkx (for graph merging logic), pydantic, pyvis (for debugging and intermediate visualization).

Ingestion Pipeline: markdownify (HTML -> Markdown), beautifulsoup4 (cleaning).

AI/LLM: langchain, langchain-community, langchain-experimental (for LLMGraphTransformer), langchain-ollama (for proper Llama 3 integration).

Create frontend/package.json (NPM) with dependencies:

Framework: next, react, react-dom.

UI Components: lucide-react (icons), clsx, tailwind-merge.

Rendering: react-markdown (for streaming AI text), remark-gfm (for tables).

Setup Script: Ensure .devcontainer/setup.sh handles the poetry install and npm install for these specific lists.

Acceptance Criteria:

[ ] poetry show inside /backend lists langchain-experimental and markdownify.

[ ] npm list inside /frontend lists react-markdown.

[ ] Llama 3 model is verified working via curl.

Quality Gates:

bash .devcontainer/setup.sh runs successfully.

python -c "import langchain_experimental; import markdownify; print('Deps OK')" returns "Deps OK".

### **US-002: Define Pydantic Graph Models (Python)**

**Description:** Create strict Pydantic models to enforce the schema for Nodes (Entities) and Edges (Relationships).
**Tasks:**

1. Create `backend/app/schemas.py`.
2. Define `GraphNode` (id, type, description).
3. Define `GraphEdge` (source, target, relation_type, description).
**Acceptance Criteria:**

* [ ] Schema enforces Entity Types: `["Field Editor", "Data Type", "Form Component", "Field", "Database Column", "Validation Rule"]`.
* [ ] Schema enforces Relationship Types: `["CONFIGURES", "MAPPED_TO", "RENDERS", "DEPENDS_ON", "STORED_AS"]`.
**Quality Gates:**
* `poetry run pytest tests/test_schemas.py` -> Passes validation logic.

---

## **Phase 2: Backend Ingestion Pipeline (Python)**

### **US-003: HTML to Semantic Markdown Conversion**

**Description:** Implement cleaning module using `markdownify`.
**Tasks:**

1. Implement `clean_and_convert(html: str) -> str`.
2. Strip `<nav>`, `<footer>`, `<script>`.
3. Convert HTML tables to Markdown pipes `|`.
**Quality Gates:**

* `poetry run pytest tests/test_converter.py` -> Output contains Markdown table syntax.

### **US-004: Header-Based Chunking Strategy**

**Description:** Implement `MarkdownHeaderTextSplitter` logic.
**Tasks:**

1. Implement `chunk_markdown(text: str) -> List[Document]`.
2. Inject metadata: `{'h1': 'Title', 'h2': 'Section'}`.
3. Prepend context string: `--- Context: Title > Section ---`.
**Quality Gates:**

* `poetry run pytest tests/test_chunking.py` -> Assert chunk metadata matches input headers.

### **US-005: Local LLM Extraction Service**

**Description:** Implement extraction service using **Ollama (Llama 3)**.
**Tasks:**

1. Implement `extract_graph_from_chunk(chunk: str)`.
2. Use `LangChain` or `Ollama` python client to send prompts to `http://ollama:11434`.
3. Force JSON mode in Llama 3 prompt ("Return strictly valid JSON...").
**Acceptance Criteria:**

* [ ] Service accepts text string, returns `KnowledgeGraph` object.
* [ ] Validates output against Pydantic schema; retries if JSON is malformed.
**Quality Gates:**
* `poetry run pytest tests/test_extraction.py` -> Live Ollama call returns valid JSON schema.

## **Phase 3: Backend API (Python/FastAPI)**

### **US-006: Graph Merging & Bi-Directional Linking**

**Description:** Implement the merging logic to combine mini-graphs from individual chunks into a Master Graph. Critically, every Node in the Master Graph must be "tagged" with the IDs of the chunks where it was found (`source_chunk_ids`).
**Tasks:**

1. **Chunk ID Assignment:** Ensure every `Document` chunk generated in *US-004* has a unique UUID (e.g., `chunk_12`).
2. **Graph Tagging Loop:**
* When adding a Node (e.g., "Field Editor") to the Master Graph:
* **If Node is new:** Create it and set property `source_chunk_ids = [current_chunk_id]`.
* **If Node exists:** Append `current_chunk_id` to the existing list (deduplicate).

Description: Implement the ingestion logic. Instead of separating graph and vectors, we create a "Chunk Node" for every piece of text and link extracted entities to it. Tasks:

Define Schema:

Chunk Node: Labels ['Chunk', 'Document']. Properties: text (string), embedding (vector), source_id (string).

Entity Node: Labels ['Entity', 'Field Editor', etc].

Relation: (Entity) -[:MENTIONED_IN]-> (Chunk).

Ingestion Loop:

Generate embedding for the chunk text (using Ollama/Llama3).

Extract Entities (LLM).

Cypher Query:

Cypher
// 1. Create the Chunk with Vector
MERGE (c:Chunk {id: $chunk_id})
SET c.text = $text, c.embedding = $embedding_vector

// 2. Link Entities to this Chunk
MERGE (e:Entity {id: $entity_id})
MERGE (e)-[:MENTIONED_IN]->(c)
Create Vector Index:

Run once: CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS FOR (c:Chunk) ON (c.embedding) OPTIONS {indexConfig: {vector.dimensions: 4096, vector.similarity_function: 'cosine'}} (Note: Llama3 dim is 4096).

Acceptance Criteria:

[ ] A single Neo4j database contains both the Knowledge Graph and the Vector Index.

[ ] Can perform a vector search query: CALL db.index.vector.queryNodes('chunk_embeddings', 5, $query_embedding). 

Quality Gates:

pytest tests/test_ingestion.py -> Ingest a doc, then run a vector search in Neo4j to find it.

To push data from LLMGraphTransformer to Neo4j, you use the add_graph_documents method provided by the Neo4jGraph class in LangChain. 

---

## **Phase 3: Backend API (Python/FastAPI)**

*(Completely rewritten US-007 to match your detailed 4-step flow)*

### **US-007: Graph-Enhanced Hybrid Retrieval Strategy**

**Description:** Implement the sophisticated retrieval logic that uses the Graph for "Reasoning" (finding connections) and the Vector Store for "Evidence" (getting the text).
**Tasks:**

**Step A: Entity Extraction (The "Search Terms")**

1. Implement a lightweight LLM call (or Keyword Extractor) to parse the User Query.
2. **Input:** "How does the system map fields to the database?"
3. **Output:** `["Field", "Database", "Map"]`.

**Step B: Graph Traversal (The "Reasoning" Layer)**

1. **Node Lookup:** Search the Neo4j/NetworkX graph for nodes matching the extracted entities (fuzzy match).
2. **Expansion:** For every hit (e.g., "Field"), traverse 1 hop to find connected neighbors.
* *Discovery:* Finds edge `(Field) --[MAPPED_TO]--> (Database Column)`.


3. **Edge Collection:** Collect the text descriptions from these edges (e.g., "Fields are mapped to columns via...").

**Step C: Parent Chunk Retrieval (The "Evidence" Layer)**

1. **ID Harvesting:** From the *Nodes* found in Step B, extract all unique `source_chunk_ids`.
2. **Fetch:** Query the Vector Store (by ID, not similarity) to retrieve the full text content for `chunk_12`, `chunk_45`, etc.
* *Why:* This ensures we get the *exact* paragraph where "Field" and "Database" were discussed, even if the user didn't use the exact keywords from that paragraph.



**Step D: Context Assembly & Generation**

1. Construct the Final System Prompt with two distinct sections:
* `--- GRAPH KNOWLEDGE ---`: The high-level relationships found in Step B.
* `--- SOURCE DOCUMENTS ---`: The raw text chunks fetched in Step C.


2. Send to LLM (Ollama/Llama 3) for the final answer.

**Acceptance Criteria:**

* [ ] **Reasoning Test:** If User asks about "Field Editor", the system includes context about "Data Types" (because they are connected neighbors), even if the user didn't say "Data Type".
* [ ] **Evidence Test:** The response cites specific details found in the text chunks (e.g., "It uses Int32").
* [ ] **Traceability:** The API response includes a `sources` array listing the chunks used.
**Quality Gates:**
* `curl -X POST /chat` with a complex query returns a detailed answer.
* Logs show: `Extracted Entities -> Graph Hits -> Chunk IDs Fetched -> Final Prompt`.

---

## **Phase 4: Frontend UI (Node.js)**

### **US-008: Next.js Chat Interface**

**Description:** Build the chat UI.
**Tasks:**

1. Configure Next.js to run on port 3030.
2. Create Chat Component (Input + Message List).
3. Render Markdown responses.
4. the thing talks to the ollama endpoint!
**Quality Gates:**

* `npm run dev` -> Accessible at `http://localhost:3030`.


### **US-009: Frontend Integration & Visualization**

**Description:** Update the chat interface to display the retrieval process transparency (optional but helpful for debugging/trust).
**Tasks:**

1. Parse the API response to separate the "Answer" from the "Sources".
2. Display the "Answer" in the main chat bubble.
3. (Optional) Display a "Reasoning" collapsible section showing:
* "Found Entities: Field, Database"
* "Used Graph Connections: Field -> Database Column"
**Acceptance Criteria:**



* [ ] UI shows the final answer clearly.
* [ ] UI indicates which sources were used (e.g., "Sources: Field Editor Docs, Database Docs").
