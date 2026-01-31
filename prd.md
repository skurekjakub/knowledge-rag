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

1. Create `.devcontainer/setup.sh` to install Poetry/NPM deps and trigger `ollama pull llama3`.
2. Configure `devcontainer.json` to map host ports `9474` (Neo4j) and `11534` (Ollama).
3. Create `.env` file with `NEO4J_URI=bolt://db:7687` and `OLLAMA_BASE_URL=http://ollama:11434`.
**Acceptance Criteria:**

* [ ] "Reopen in Container" successfully builds the environment.
* [ ] Backend `poetry install` and Frontend `npm install` run automatically.
* [ ] Llama 3 model is available (verify via `curl http://ollama:11434/api/tags` inside container).
**Quality Gates:**
* `bash .devcontainer/setup.sh` runs without error.
* `ping db` and `ping ollama` succeed from inside the VS Code terminal.

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

### **US-006: Graph Merging & Neo4j Ingestion**

**Description:** Merge mini-graphs and push to Neo4j.
**Tasks:**

1. Implement `merge_graphs` using `NetworkX` (merge nodes by ID, append edge descriptions).
2. Implement `Neo4jConnector` using `neo4j` driver.
**Quality Gates:**

* Run ingestion script.
* Check `http://localhost:9474` (Host Browser) -> `MATCH (n) RETURN count(n)` > 0.

---

## **Phase 3: Backend API (Python/FastAPI)**

### **US-007: FastAPI Query Endpoint**

**Description:** Create the RAG API endpoint.
**Tasks:**

1. Setup FastAPI on port 8080 (mapped internal).
2. Create `POST /chat`.
3. Logic: Vector Search + Graph Traversal -> Ollama Answer Generation.
**Acceptance Criteria:**

* [ ] Endpoint accepts `{"query": "How do I create a field?"}`.
* [ ] Returns JSON `{"answer": "...", "sources": [...]}`.
**Quality Gates:**
* `curl -X POST http://localhost:8080/chat -d '{"query": "test"}'` -> Returns 200 OK.

---

## **Phase 4: Frontend UI (Node.js)**

### **US-008: Next.js Chat Interface**

**Description:** Build the chat UI.
**Tasks:**

1. Configure Next.js to run on port 3030.
2. Create Chat Component (Input + Message List).
3. Render Markdown responses.
**Quality Gates:**

* `npm run dev` -> Accessible at `http://localhost:3030`.

### **US-009: Integration**

**Description:** Connect Frontend to Backend.
**Tasks:**

1. Proxy API requests to `http://localhost:8080`.
**Acceptance Criteria:**

* [ ] User asks question in UI -> Answer is generated by Llama 3 (via Python).
**Quality Gates:**
* End-to-end manual test of a documentation query.