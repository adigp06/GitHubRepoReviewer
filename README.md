# 🤖 Autonomous GitHub Repository Architecture Reviewer

An intelligent multi-agent pipeline designed to analyze public GitHub repositories. By connecting to the remote GitHub API, this system inspects directory structures, cleans noise, and chunks files to respect context limits, running multiple isolated agents in parallel to deliver a structured engineering report.

---

## 🎯 Project Objective
To build an automated code review system that converts a raw, remote GitHub repository into clean, AI-readable context. The goal is to evaluate codebases across quality of architecture, documentation, testing, code quality, and dependencies without exceeding LLM context windows or incurring heavy network and storage overhead.

---

## 🏗️ Approach & Methodology

### 1. URL Parser & Virtual Indexer (`url_parser.py`, `indexer.py`)
* **How it works:** The system extracts the repository owner and name from a public URL and queries GitHub's `git/trees` API recursively.
* **But Why?:** This bypasses running a heavy, network-draining `git clone` on local storage. It treats the remote codebase as a fast, in-memory structural index over the wire.

### 2. Context ETL Pipeline (`cleaner.py`, `preprocessor.py`)
* **How it works:** Raw directory structures contain massive token noise (like `.png` or `.ipynb` assets) that waste context space. The system strips these out. A sliding-window text chunker then slices files into 4,000-character segments with a 400-character overlap.
* **But Why?:** The 400-character overlap prevents structural code syntax or function declarations from being severed down the middle across chunk boundaries, preserving critical logical context for the agents.

### 3. Native ReAct (Reasoning & Acting) Loop (`agent_core.py`)
* **How it works:** The planner agent evaluates user requests and generates a precise internal `Thought` followed by a structured JSON `Action`. 
* **But Why?:** Built natively without high-level framework wrappers (like LangChain or LangGraph) to ensure absolute execution transparency, minimal dependency bloat, and total control over state data.

### 4. Parallel Swarm with Token Backoff (`agent_core.py`)
* **How it works:** The context-safe code layout is dispatched concurrently to 5 specialized evaluation agents:
  * **Architecture Reviewer:** Evaluates project structure and scalability.
  * **Documentation Reviewer:** Checks onboarding clarity, examples, and README quality.
  * **Testing Reviewer:** Evaluates test coverage and strategy reliability.
  * **Code Quality Reviewer:** Judges readability and maintenance metrics.
  * **Dependency Reviewer:** Identifies external library bloat and structural complexity.
* **Additional Modification:** A deterministic 2-second delay (`time.sleep(2)`) is introduced between agent iterations to act as a rate-limit backoff, preventing 429 token-per-minute exhaustion limits on simultaneous API payloads.

### 5. Final Aggregator Judge
* **How it works:** Individual agent outputs are merged into a single payload for the **Lead Systems Judge**, which compiles the remarks into a beautifully formatted markdown report containing an overall readiness score and a prioritized action list.

---

## ⚠️ Assumptions, Limitations & Observations

### Assumptions
* **Main Branch Default:** The indexer assumes the core codebase resides in the default `main` branch when making recursive tree calls. 

### Limitations
* **Upstream Data Cleaning Constraints:** To optimize the token window, `cleaner.py` completely discards binary assets, `.png` files, `.lock` dependency files, and Jupyter Notebooks (`.ipynb`). While this significantly drops context bloat, it means the agents will not evaluate content with respect to such data
* **Free-Tier API Rate Windows:** Because five specialist agents are invoked in parallel, running the system on massive, multi-thousand-file codebases can occasionally push the boundaries of the free-tier Gemini API's Input Tokens Per Minute (TPM) quota.
* **Context Overlap Boundaries:** The sliding-window preprocessor slices text strictly by character length (4,000 characters). While the 400-character overlap maintains readability, a massive individual file may still see minor semantic fragmentation if an engineering pattern spans across multiple chunk boundaries.

### Some Key Notes
* **Deterministic Backoff Success:** Introducing a concrete 2-second rate-limiting delay (`time.sleep(2)`) between concurrent agent iterations completely eliminated `429 Resource Exhausted` API spikes, proving that basic structural throttling is sufficient for managing simple multi-agent parallel swarms.
* **State Preservation Error Mitigation:** Isolating the output of `preprocess_repository_assets` cleanly within `repo_context_str` instead of blending raw dictionary metadata ensured that downstream agents evaluated actual logic segments rather than un-chunked API telemetry strings.

