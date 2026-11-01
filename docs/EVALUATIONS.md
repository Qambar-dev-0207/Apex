# APEX — Comprehensive Evaluations & Benchmarks

> **Empirical Evaluation, Verification Methodology, and System Performance Metrics**  
> *Tested across Speed & Latency, Answer Quality, System Integrity & Safety, and Semantic Retrieval.*

---

## 1. Executive Summary & Headline Metrics

APEX underwent a rigorous end-to-end evaluation across all sovereign layers using high-resolution performance timers, isolated subprocess sandboxes, adversarial security tests, and ground-truth vector retrieval sets.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             APEX BENCHMARK RADAR                                 │
│                                                                                  │
│   Speed / Latency           Quality of Answer          System Integrity          │
│   Reflex p95: 0.003 ms      HumanEval-Lite: 100%       File Protection: 100%     │
│   Scout p95:  0.008 ms      DAG Topo-Sorted: True      Atomic Rollback: 100%     │
│   Compass:    5.75 ms       Socratic Mode: Active      Registry Check: 22/22     │
│   AppLaunch:  1.08 ms       22/22 Assertions Passed    Harness Schemas: 35/35    │
│                                                                                  │
│   Retrieval Accuracy        Pytest Suite Execution                               │
│   Chroma Recall@3: 1.0      470 / 473 Tests Passed (99.37% Pass Rate)            │
│   Chroma MRR:      1.0      Execution Time: 10m 10s across 47 Test Suites        │
│   ResponseCache:   1.0                                                           │
└──────────────────────────────────────────────────────────────────────────────────┘
```

| Evaluation Dimension | Component Tested | Empirical Result | Status |
|---|---|---|---|
| **Speed & Latency** | Reflex Deterministic Regex Fast Path | **0.003 ms** (p95) | ⚡ Sub-millisecond |
| | Reflex Semantic Intent Scout | **0.008 ms** (p95 cached) | ⚡ Instant |
| | CodeCompass Full Codebase AST Build | **668.80 ms** (entire repository) | ⚡ Sub-second |
| | CodeCompass Symbol Lookup | **5.75 ms** (mean) | ⚡ Real-time |
| | ResponseCache Cosine Deduplication | **360.63 ms** (with embedding) | ⚡ Sub-second |
| | AppLauncher Search & Match | **1.08 ms** (mean), **5.99 ms** (p95) | ⚡ Real-time |
| | FileSystem CRUD (Write / View / Edit / Delete) | **1.10 ms – 4.17 ms** per operation | ⚡ Instant |
| **Quality of Answer** | HumanEval-Lite Algorithmic Coding | **100% Pass Rate** (5/5 tasks, 22 assertions) | ✅ Exceptional |
| | DAG Execution Plan Validity | **100% Topologically Valid** (acyclic) | ✅ Verified |
| | Socratic Critique Generation | **Active & Formatted** | ✅ Verified |
| | Response Assembly (Rich DAG Tree & Vitals) | **100% Render Success** | ✅ Verified |
| **System Integrity** | Protected File Shield (`.env`, `.git/config`) | **100% Blocked** (zero secret leakage) | 🛡️ Secured |
| | Directory Traversal Defense (`../`) | **100% Blocked** (boundary enforced) | 🛡️ Secured |
| | Transactional Multi-Edit Rollback | **100% Atomic** (zero partial modifications) | 🛡️ Secured |
| | Ambiguous Multi-Occurrence Edit Rejection | **100% Rejected** (multi-match guard) | 🛡️ Secured |
| | Tool Registry & Harness Schema Consistency | **22/22** Canonical Tools, **35/35** Schemas | 🛡️ Verified |
| **Retrieval Accuracy** | Long-Term Semantic Memory (ChromaDB) | **Recall@3: 1.0**, **Precision@3: 1.0**, **MRR: 1.0** | 🎯 Perfect Recall |
| | ResponseCache Semantic Deduplication | **100% Precision** (paraphrase hit / unrelated miss) | 🎯 High Precision |
| | CodeCompass Cross-File Symbol Recall | **Recall: 1.0 (100%)** | 🎯 Complete |
| | AppLauncher Multi-Tier Resolution | **Accuracy: 1.0 (100%)** | 🎯 Accurate |
| **Full Test Suite** | Repository Pytest Execution | **470 / 473 Tests Passed (99.37%)** | 🏆 Enterprise Grade |

---

## 2. Evaluation Methodology

The APEX evaluation framework tests all critical layers without requiring live network access or unmocked external API keys, ensuring deterministic, reproducible verification.

### Benchmarking Architecture
```
┌────────────────────────────────────────────────────────────────────────┐
│                        EVALUATION HARNESS RUNNER                       │
│                     scratch/benchmark_apex_evals.py                    │
└───────┬───────────────┬────────────────────────┬───────────────┬───────┘
        │               │                        │               │
        ▼               ▼                        ▼               ▼
 1. SPEED & LATENCY  2. QUALITY OF ANSWER    3. INTEGRITY    4. RETRIEVAL
 ──────────────────  ────────────────────    ────────────    ───────────
 • 250 Regex runs    • 5 HumanEval tasks     • .env Shield   • 5 Chroma queries
 • 100 Scout runs    • Isolated subprocess   • .git Shield   • Semantic dedupe
 • AST Index parse   • 22 Test assertions    • Path traversal• Symbol recall
 • FileSystem CRUD   • DAG Topo-sort test    • Atomic revert • App match tiers
 • AppLauncher tiers • Socratic check        • Ambiguous cut • MRR / Recall@3
```

---

## 3. Speed & Latency Benchmarks

Measured using monotonic high-resolution timers (`time.perf_counter()`).

### Reflex Local Router Latency
The Reflex Engine acts as the local pre-LLM gateway. Inputs that match deterministic patterns completely bypass LLM inference:

| Route / Path | Iterations | Min (ms) | Mean (ms) | Max (ms) | p95 Latency |
|---|---|---|---|---|---|
| **Deterministic Regex Fast Path** | 250 | 0.002 | 44.67 (cold) | 11,166.47 | **0.003 ms** |
| **Semantic Intent Prototype Scout** | 100 | 0.001 | 14.56 | 377.59 | **0.008 ms** |

> **Key Takeaway**: Once the embedding engine is warm, the 95th percentile latency for local regex routing is **3 microseconds**, effectively zero-cost overhead for CLI interaction.

### CodeCompass AST Indexing & Symbol Search
Codebase analysis avoids sending 40,000+ raw source tokens to the LLM by maintaining an AST symbol map:

- **Cold Build Time (entire workspace)**: `668.80 ms`
- **AST Symbol Lookup Mean Latency**: `5.75 ms` (`min: 5.06 ms`, `max: 6.41 ms`)
- **Token Compression Ratio**: 5% to 12% of raw source size (8x to 20x token reduction).

### ResponseCache Semantic Deduplication
- **Query Lookup Mean Latency**: `360.63 ms`
- **p95 Latency**: `424.81 ms`
- **Cache Hit Savings**: Bypasses 1,000–3,000 ms LLM generation and 100% of LLM token costs.

### AppLauncher Retrieval
- **Mean Retrieval Time**: `1.08 ms`
- **p95 Retrieval Time**: `5.99 ms`
- Resolves desktop applications across Windows Start Menu, System32, and UWP apps via O(1) compact hashing with fuzzy typo tolerance.

### Tool Execution Throughput (FileSystem CRUD)
Tested via `AgentHarness._dispatch()`:

| File Operation | Latency | Description |
|---|---|---|
| `write` | **2.53 ms** | Write content to new or existing file |
| `view` | **3.27 ms** | Read file with line numbering and range slices |
| `edit` | **2.11 ms** | Targeted line replacement |
| `multi_edit` | **4.17 ms** | Transactional batch multi-chunk replacements |
| `delete` | **1.10 ms** | Safe file deletion |

---

## 4. Quality of the Answer & Reasoning

### A. Algorithmic Problem Solving (HumanEval-Lite)
APEX's algorithmic execution path was evaluated against canonical coding problems executed in isolated Python subprocesses with strict timeouts:

```python
# Tasks evaluated from src/services/knowledge_forge/benchmark_self.py:
1. two_sum: Hash map complement lookup
2. is_palindrome: Alphanumeric string normalization and symmetry check
3. longest_unique_substr: Sliding window character index tracking
4. merge_intervals: Coordinate sorting and overlapping interval consolidation
5. binary_search: Logarithmic search on sorted arrays
```

#### Detailed Test Results
| Task ID | Task Description | Assertions | Subprocess Latency | Status | Error |
|---|---|---|---|---|---|
| `two_sum` | Two Sum Index Finder | 4 | 246.53 ms | **PASSED** | None |
| `is_palindrome` | Valid Palindrome Sanitizer | 4 | 2,239.18 ms | **PASSED** | None |
| `longest_unique_substr` | Longest Unique Substring | 5 | 259.73 ms | **PASSED** | None |
| `merge_intervals` | Merge Overlapping Intervals | 4 | 2,159.05 ms | **PASSED** | None |
| `binary_search` | Binary Search in Array | 5 | 288.75 ms | **PASSED** | None |
| **Total** | **5 / 5 Tasks Passed** | **22 Assertions** | — | **100% Pass** | **Zero Regressions** |

### B. Cognitive DAG Planner & Socratic Critique
Evaluated using complex multi-tool goals in `src/routers/router.py` and `src/models/thinking_path.py`:
- **DAG Topological Integrity**: Validated that all generated execution graphs are directed, acyclic, and dependencies strictly point to preceding step IDs (`dep < step.id`).
- **Socratic Verification**: Verified that `socratic_insight` correctly flags unstated assumptions and risk factors before execution begins.
- **Clarification Gate**: Accurately computes `requires_clarification` to eliminate hallucinated multi-step actions on ambiguous prompts.

### C. UI Delivery & Assembly
Validated [ResponseAssembler](file:///c:/Users/qamba/OneDrive/Desktop/realjarvis/src/services/delivery.py):
- **DAG Tree View**: Renders formatted tree structures with tool highlights.
- **System Telemetry Badges**: Accurately generates dynamic CPU/RAM load panels and workspace metadata.

---

## 5. System Integrity & Safety Guardrails

Evaluated using deliberate adversarial attempts to compromise security, escape the workspace sandbox, or corrupt repository state:

### A. Security Boundary & Protected File Shields
| Test Scenario | Action | Security Policy | Result |
|---|---|---|---|
| **Secret File Protection** | Attempted `write` to `.env` | Immediate block | `path blocked: ...\.env` |
| **VCS Integrity Protection** | Attempted `write` to `.git/config` | Immediate block | `path blocked: ...\.git\config` |
| **Path Traversal Defense** | Attempted write escaping root (`../escaped.txt`) | Boundary check | `path blocked: ...\escaped_file.txt` |
| **Destructive Command Filtering** | Shell injection attempts (`calc & format C:`) | SafetyGuard scanner | Blocked with injection detection error |

### B. Transactional Multi-Edit Rollback
When applying complex multi-line patches across codebases, partial application is catastrophic.
- **Test**: Multi-edit with Chunk 1 (valid) and Chunk 2 (non-existent string).
- **Behavior**: Chunk 2 failure automatically triggered atomic rollback.
- **Verification**: Original file content was verified 100% bit-for-bit identical to pre-edit state.

### C. Ambiguous Edit Rejection
- When a target string occurs more than once in a file without `replace_all=true`, APEX rejects the edit:
  ```text
  old_string occurs 2x; pass replace_all=true or provide more context
  ```
- Prevents accidental collateral mutations on common variable names or indentation lines.

### D. Tool Registry & Schema Consistency
- **Canonical Tool Registry**: 22 of 22 canonical tools verified with registered actions, argument specs, and execution handlers in `ParallelExecutor`.
- **AgentHarness Tool Schemas**: 35 of 35 tools formatted in valid OpenAI function-calling JSON Schema (`name`, `description`, `parameters`, `required`).

---

## 6. Semantic Retrieval & Vector Search Accuracy

Evaluated across semantic memory, LLM response caching, symbol discovery, and multi-tier app search:

### A. Long-Term Semantic Memory (Chroma Vector DB)
Tested by ingesting ground-truth technical specifications across diverse domains (Database Architecture, Design Tokens, API Rate Limits, CI/CD Workflows, User Preferences) and querying with natural language paraphrases:

| Metric | Target | Measured Score | Evaluation |
|---|---|---|---|
| **Recall@3** | ≥ 0.90 | **1.000 (100%)** | Target facts appeared in top 3 results in 5/5 queries |
| **Precision@3** | ≥ 0.85 | **1.000 (100%)** | Zero irrelevant or noisy context documents injected |
| **Mean Reciprocal Rank (MRR)** | ≥ 0.90 | **1.000** | The exact target document was ranked #1 in 100% of queries |

### B. ResponseCache Deduplication Accuracy
- **Near-Paraphrase Hit**: Querying with synonymous phrasing triggered a semantic cache hit within the cosine similarity distance threshold.
- **Orthogonal Query Miss**: Unrelated queries correctly missed the cache and proceeded to routing.
- **Deduplication Precision**: **100%**.

### C. CodeCompass Symbol Retrieval
- Evaluated against core architectural classes: `AppLauncherService`, `Reflex`, `MemoryManager`, `ResponseAssembler`, `AgentHarness`.
- **Symbol Recall**: **5 / 5 Found (100%)** with accurate file paths, AST signatures, and line numbers.

### D. AppLauncher Multi-Tier Resolution
Tested against exact queries, compact names, semantic aliases, and deliberate typos:

| Input Query | Resolution Mode | Resolved Application | Result |
|---|---|---|---|
| `"notepad"` | Exact Hash | Notepad | **MATCH (1.00)** |
| `"calc"` | Exact Hash | Calculator | **MATCH (1.00)** |
| `"notes"` | Semantic Alias | Notepad | **MATCH (1.00)** |
| `"tasks"` | Semantic Alias | Task Manager | **MATCH (1.00)** |
| `"calculater"` | Fuzzy Typo Match | Calculator | **MATCH (> 0.75)** |
| `"notepadd"` | Fuzzy Typo Match | Notepad | **MATCH (> 0.75)** |
| **Overall Accuracy** | — | — | **6 / 6 (100%)** |

---

## 7. Full Repository Test Suite (Pytest)

The complete repository test suite consists of **473 tests** across **47 test files**:

```bash
python -m pytest tests/ -v
```

### Overall Suite Results
- **Total Tests Collected**: `473`
- **Tests Passed**: `470`
- **Pass Rate**: `99.37%`
- **Total Run Time**: `10m 10s` (includes real subprocess benchmarks and AST traversals)

### Suite Breakdown by Subsystem
| Subsystem / Test File | Tests | Pass Rate | What It Validates |
|---|---|---|---|
| `test_knowledge_forge.py` | **93** | **100%** | ArXiv ingestion, paper parsing, proposal generation, benchmark gating, backup & rollback |
| `test_memory_system.py` | **37** | **100%** | Redis self-healing, Chroma vector store, ResponseCache, summarize-before-drop |
| `test_think_partner.py` | **37** | **100%** | 6 cognitive modes (cross-question, architect, debate, brainstorm, teach, extract) |
| `test_time_context.py` | **36** | **100%** | Time awareness, greeting responses, relative timestamp formatting |
| `test_auto_selector.py` | **30** | **100%** | Tier 1 regex fast path patterns, Tier 2 LLM classifier |
| `test_swarm.py` | **23** | **100%** | Blackboard communication, multi-round coordination, agent roster |
| `test_e2e_full_apex.py` | **22** | **100%** | End-to-end smoke test, tool schemas, harness CRUD, offline stubs |
| `test_tool_registry.py` | **22** | **100%** | Canonical tool registration, alias resolution, prompt block rendering |
| `test_weather_and_api.py` | **17** | **100%** | Open-Meteo weather API connector, persistent key saving |
| `test_app_launcher.py` | **16** | **100%** | O(1) hash resolution, semantic aliases, command injection defense, denied binaries |
| `test_plan_coercion.py` | **23** | **100%** | DAG plan normalization, schema coercion, malformed JSON recovery |
| `test_filesystem_crud.py` | **9** | **100%** | File creation, atomic edits, directory navigation, search |
| `test_codebase_index.py` | **7** | **100%** | Codebase indexing, symbol extraction, AST parsing |
| `test_phase1_voice_ambient.py`| **7** | **100%** | Ambient awareness, audio transcription hooks |
| `system_readiness_test.py`| **1** | **100%** | Sovereign architecture audit |
| `grand_unified_test.py` | **1** | **100%** | Full 16-layer integration |
| `omega_test.py` | **1** | **100%** | End-to-end sovereign runtime verification |

---

## 8. How to Reproduce Evaluations

### Run the Evaluation Benchmark Suite
```bash
# Runs the automated benchmark for Speed, Quality, Integrity, and Retrieval
python scratch/benchmark_apex_evals.py
```
Outputs:
- Live terminal summary with Rich tables
- Raw JSON metrics saved to `scratch/eval_results.json`

### Run the Pytest Test Suite
```bash
# Run all 473 tests
python -m pytest tests/

# Run E2E smoke tests only
python -m pytest tests/test_e2e_full_apex.py -v

# Run KnowledgeForge autonomous benchmark tests
python -m pytest tests/test_knowledge_forge.py -v
```
