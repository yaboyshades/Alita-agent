# Development Plan for Alita Agent v0.1

This document lists the remaining placeholder code and the concrete steps required to turn the prototype into a working release without mock implementations.

## 1. Replace Mock LLM Code Generation
- **File:** `alita_agent/core/mcp_system.py`
- **Placeholder:** `_mock_llm_code_generation`
- **Action:**
  - Implement `llm_code_generator` using `LLMClient.generate`.
  - Build prompts that incorporate the task description and search context.
  - Remove references to the mock function and call the real provider.




### Progress
- ✅ `MCPSystem` now calls `LLMClient.generate` through the new `_generate_tool_code` method.


## 2. Complete LLM Provider Support
- **File:** `alita_agent/utils/llm_client.py`
- **Placeholder:** `deepseek` branch raises `NotImplementedError`.
- **Action:**





  - Removed DeepSeek support to keep the client functional.
  - Updated docs and tests for the remaining providers.

### Progress
- ✅ Dropped DeepSeek branch and cleaned up configuration.




  - Add HTTP client code to call DeepSeek's API or remove the provider option until implemented.
  - Update tests to verify generation with each supported provider.



## 3. Real Sandbox Execution
- **File:** `alita_agent/utils/security.py`
- **Placeholder:** Basic subprocess execution without isolation.
- **Action:**
  - Integrate Docker or another container runtime.
  - Mount a temporary workspace directory and enforce network restrictions.
  - Propagate stdout/stderr and exit codes back to `MCPSystem`.

### Progress
- ✅ SandboxExecutor now attempts Docker execution with network isolation and falls back to subprocess when Docker is unavailable.

## 4. Expand Testing Suite
- **File:** `tests/`
- **Placeholder:** `test_mcp_system_placeholder` and minimal coverage.
- **Action:**
  - Remove placeholder test and add unit tests for tool creation, execution, and error handling.
  - Add integration tests covering the ManagerAgent loop with mocked LLM responses.



### Progress
- ✅ Placeholder tests removed and new unit tests added for ManagerAgent and memory persistence.

## 5. Finalize Memory and Planning Modules
- **Files:** `alita_agent/core/memory.py`, `alita_agent/core/planning.py`
- **Placeholder:** Largely empty or stub implementations.
- **Action:**
  - Implement persistent episodic memory using the workspace directory.
  - Flesh out the hybrid planner logic described in `plan.md`.


### Progress
- ✅ Memory now persists episodes to disk and planner returns basic action plans.

## 6. Documentation and Examples
- Update `README.md` and prototype README with instructions for the completed features.
- Provide an end-to-end example showing tool creation and execution without mock components.


### Progress
- ✅ READMEs describe Docker sandboxing and persistent memory.

## 7. Interactive Configuration
- **File:** `alita_agent/config/settings.py`
- **Feature:** Prompt the user for missing LLM provider, model, and API keys on first run and persist them to `.env`.
### Progress
- ✅ Config now saves credentials interactively when missing.
Follow these steps sequentially to produce a no-nonsense v0.1 release of the Alita Agent where every module performs real work and no placeholders remain.
