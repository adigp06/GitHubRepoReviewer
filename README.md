# Autonomous GitHub Repository Architecture Reviewer

An intelligentm multi agent pipeline designed to analyze public GitHub repositories. By connecting to the remote GitHub API, this system inspects directory structures, cleans noise, chunks files, to respect context limits, runs multiple isolated agents to deliver an engineering report.

---

# Basic Architecture Explanation

### 1. URL Parser & Virtual Indexer
***How it works**: System extracts the repository owner's and name from any valid public URL. it then contracts GitHub's `git/trees` API recursively.

***Reasoning:** As mentioned in the assignment prompt, it avoids making use of network draining `git clone` on local storage

### 2. Context ETL Pipeline

***How it works:**Raw directory structures typically contian massive token noise like `.png`,`.ipynb` assets which waste money and attention space. Hence, we strip the data first. a sliding window text chunker then cuts the files into manageable , 4000 character segments, and leaves a 400 character overlap between adjacent blocks. This prevents programming syntax or a function declaration from being cut straight down the middle across boundaries, so we can preserve context for the agent. 

### 3. Native ReAct Loop
**How it works:**The planner agent evaluates the user requests and generates a precise thought, followed by action. 

### 4. Parallel Swarm with Token Backoff
***How it works:**This context safe code is then sent to 5 specialized evaluation agents simultanously:
***Architecture Reviewer**(Structure and Scalability)
***Documentation Reviewer**(Onboarding, Examples, REAEDME quality)
***Testing Reviewer**(Test Coverage and Reliability)
***Code Quality**(Readibility and Maintanence metrics)
***Dependecy Reviewer**(Bloat and Structural Complexity)

### 5. Final Aggregator Judge
* The individual reviews are merged into an organized string payload and handed to a **Lead Systems Judge**, compiling the various remarks into a markdown report with an overall readiness score and prioritized action items.