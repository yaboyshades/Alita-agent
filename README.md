# 🚀 Cortex Copilot++

Supercharge GitHub Copilot with repo-aware context, automated code formatting, and testing integration—plus one-click automation commands from VS Code.

## Quick Start (GitHub Codespaces or local)

```bash
./setup.sh
python run_proxy.py

Then in VS Code:

“Developer: Reload Window”

Command Palette:

Cortex: Boost Selection

Cortex: Apply Generated Code

Cortex: Run Python Tests

Cortex: Format & Lint (Python)

Cortex: Build VS Code Extension



What’s Inside

Proxy API (FastAPI) for context-injection + code validation/formatting/testing

VS Code Extension (TypeScript) to boost prompts & apply generated code safely

Automation Endpoints: run tests, format/lint, build extension, git helpers


Health Check

Visit http://localhost:8000/health

---

## Python: Common Logging

### `cortex/common/logging.py`
```python
"""
Structured logging configuration for Cortex components.
"""
import logging
import sys
from typing import Optional, Dict, Any
import json
from datetime import datetime

class CortexJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def setup_logging(
    level: int = logging.INFO,
    json_format: bool = False,
    extra_fields: Optional[Dict[str, Any]] = None
) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    handler = logging.StreamHandler(sys.stdout)
    formatter = CortexJSONFormatter() if json_format else logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    if extra_fields:
        class ExtraFieldsFilter(logging.Filter):
            def filter(self, record):
                if not hasattr(record, 'extra'):
                    record.extra = {}
                record.extra.update(extra_fields)
                return True
        root_logger.addFilter(ExtraFieldsFilter())

def get_logger(name: str, extra: Optional[Dict[str, Any]] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if extra:
        class ExtraContextFilter(logging.Filter):
            def __init__(self, extra_fields):
                super().__init__()
                self.extra_fields = extra_fields
            def filter(self, record):
                if not hasattr(record, 'extra'):
                    record.extra = {}
                record.extra.update(self.extra_fields)
                return True
        for f in logger.filters:
            if hasattr(f, 'extra_fields') and f.extra_fields == extra:
                logger.removeFilter(f)
        logger.addFilter(ExtraContextFilter(extra))
    return logger
```
---

Python: Proxy (FastAPI) with Formatting/Testing + Automation Router

cortex/proxy/copilot_middleware.py

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os, glob, re
from cortex.common.logging import setup_logging, get_logger
from cortex.tools.formatters import format_code_with_black
from cortex.tools.testing import run_tests, run_linters
from cortex.api.endpoints.automation import router as automation_router

setup_logging()
log = get_logger("cortex.proxy")

app = FastAPI(title="Cortex Copilot Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

class AugmentIn(BaseModel):
    message: str
    context: Dict[str, Any] = {}

class AugmentOut(BaseModel):
    messages: List[Dict[str, str]]
    max_tokens: int = 4000
    temperature: float = 0.1

class ProcessIn(BaseModel):
    response: str
    original_prompt: str

class FileChange(BaseModel):
    file: str
    content: str
    description: Optional[str] = None
    formatted: bool = False
    lint_passed: bool = False

class TestResult(BaseModel):
    passed: bool
    output: str
    coverage: Optional[float] = None

class ProcessOut(BaseModel):
    original_response: str
    changes: List[FileChange]
    test_results: Optional[TestResult] = None
    lint_results: Optional[Dict[str, Any]] = None

def _list_repo_files(limit: int = 50) -> List[str]:
    files = []
    ignore_patterns = [".git/", "node_modules/", "cortex-extension/out/", "__pycache__/", ".vscode/"]
    patterns = ["**/*.py", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx", "**/*.json", "**/*.md", "**/*.yml", "**/*.yaml"]
    for pattern in patterns:
        for file in glob.glob(pattern, recursive=True):
            if not any(ignored in file for ignored in ignore_patterns):
                files.append(file)
    return files[:limit]

def _build_system_message(situation_brief: str, relevant_files: List[str]) -> str:
    files_str = "\n".join(f"- {f}" for f in relevant_files[:10])
    return f"""You are a coding copilot. Use the situation brief and relevant files to produce precise, minimal diffs.

Situation Brief:
{situation_brief}

Relevant files in this repository:
{files_str}

Rules:
- Always include code blocks labeled with '# file: <path>' on the first line
- Optional '# desc: <description>' on the second line
- Keep changes minimal and focused
- Maintain existing code style and patterns
- Include tests if changing behavior
- Follow PEP 8 and project coding standards
"""

def _simple_situation_brief() -> str:
    return "Current priorities: address failing tests, improve developer experience, maintain code quality. Prefer small, focused changes."

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cortex-proxy"}

@app.post("/v1/augment-prompt", response_model=AugmentOut)
async def augment_prompt(inp: AugmentIn):
    user_msg = inp.message
    situation_brief = _simple_situation_brief()
    files = _list_repo_files(limit=20)
    sys_msg = _build_system_message(situation_brief, files)
    log.info("augment_prompt", extra={"user_msg_length": len(user_msg), "file_count": len(files), "top_files": files[:5]})
    return AugmentOut(
        messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": user_msg}],
        max_tokens=4000, temperature=0.1
    )

@app.post("/v1/process-response", response_model=ProcessOut)
async def process_response(inp: ProcessIn):
    text = inp.response
    changes: List[FileChange] = []
    pattern = r"```(?:\w+)?\n(.*?)```"
    for match in re.finditer(pattern, text, flags=re.DOTALL):
        block = match.group(1).strip()
        lines = block.splitlines()
        if not lines:
            continue
        first_line = lines[0].strip()
        if first_line.startswith("# file:"):
            file_path = first_line.split(":", 1)[1].strip()
            description = None
            content_start = 1
            if len(lines) > 1 and lines[1].strip().startswith("# desc:"):
                description = lines[1].split(":", 1)[1].strip()
                content_start = 2
            content = "\n".join(lines[content_start:])

            formatted_content = content
            formatting_success = True

            if file_path.endswith('.py'):
                try:
                    formatted_content = format_code_with_black(content)
                    formatting_success = True
                except Exception as e:
                    log.warning("black_formatting_failed", extra={"error": str(e)})
                    formatting_success = False

                try:
                    lint_result = run_linters(content, file_path)
                    lint_passed = lint_result.get("ruff", {}).get("success", False)
                except Exception as e:
                    log.warning("ruff_linting_failed", extra={"error": str(e)})
                    lint_passed = False
            else:
                lint_passed = True

            changes.append(FileChange(
                file=file_path, content=formatted_content, description=description,
                formatted=formatting_success, lint_passed=lint_passed
            ))

    test_results = None
    if any(change.file.endswith('.py') for change in changes):
        try:
            r = run_tests()
            test_results = TestResult(passed=r["passed"], output=r["output"], coverage=r.get("coverage"))
        except Exception as e:
            log.error("test_execution_failed", extra={"error": str(e)})

    log.info("process_response", extra={"changes_count": len(changes), "test_run": test_results is not None})
    return ProcessOut(original_response=text, changes=changes, test_results=test_results)

# Mount automation API
app.include_router(automation_router)
```
---

Python: Tools (Formatting & Testing)

cortex/tools/formatters.py

```python
import subprocess
import tempfile
from typing import Dict, Any
from cortex.common.logging import get_logger

logger = get_logger("cortex.tools.formatters")

def format_code_with_black(code: str) -> str:
    """Format Python code using black"""
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    try:
        result = subprocess.run(['black', '--quiet', '--line-length', '88', temp_file],
                                capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            logger.warning("black_formatting_failed", extra={"stderr": result.stderr})
            return code
        with open(temp_file, 'r', encoding='utf-8') as f:
            return f.read()
    except subprocess.TimeoutExpired:
        logger.warning("black_formatting_timeout")
        return code
    except Exception as e:
        logger.error("black_formatting_error", extra={"error": str(e)})
        return code
    finally:
        try: os.unlink(temp_file)
        except: pass

def format_code_with_ruff(code: str, file_path: str) -> Dict[str, Any]:
    """(Optional) Example: format/check with ruff"""
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    try:
        check = subprocess.run(['ruff', 'check', '--select', 'I', temp_file],
                               capture_output=True, text=True, timeout=30)
        if check.returncode != 0:
            fix = subprocess.run(['ruff', 'format', temp_file],
                                 capture_output=True, text=True, timeout=30)
            if fix.returncode == 0:
                with open(temp_file, 'r', encoding='utf-8') as f:
                    return {"success": True, "formatted": True, "content": f.read()}
        return {"success": True, "formatted": False, "content": code}
    except subprocess.TimeoutExpired:
        logger.warning("ruff_formatting_timeout")
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        logger.error("ruff_formatting_error", extra={"error": str(e)})
        return {"success": False, "error": str(e)}
    finally:
        try: os.unlink(temp_file)
        except: pass
```

cortex/tools/testing.py

```python
import subprocess
import json
from typing import Dict, Any
from cortex.common.logging import get_logger

logger = get_logger("cortex.tools.testing")

def run_tests(test_path: str = "", coverage: bool = True) -> Dict[str, Any]:
    """Run pytest tests and return results"""
    cmd = ["pytest", "-v", "--tb=short"]
    if coverage:
        cmd.extend(["--cov", ".", "--cov-report", "json"])
    if test_path:
        cmd.append(test_path)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        coverage_data = None
        if coverage and (result.returncode in (0, 5)):
            try:
                with open("coverage.json", "r", encoding="utf-8") as f:
                    coverage_json = json.load(f)
                    coverage_data = coverage_json.get("totals", {}).get("percent_covered")
            except FileNotFoundError:
                pass
            finally:
                try:
                    import os
                    os.remove("coverage.json")
                except:
                    pass
        return {
            "success": result.returncode == 0,
            "passed": result.returncode == 0,
            "output": result.stdout + result.stderr,
            "coverage": coverage_data
        }
    except subprocess.TimeoutExpired:
        logger.error("test_execution_timeout")
        return {"success": False, "passed": False, "output": "Test execution timed out after 2 minutes", "coverage": None}
    except Exception as e:
        logger.error("test_execution_error", extra={"error": str(e)})
        return {"success": False, "passed": False, "output": f"Test execution error: {str(e)}", "coverage": None}

def run_linters(code: str, file_path: str) -> Dict[str, Any]:
    """Run linters on code and return results (Ruff + Mypy on demand)"""
    import os, tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    try:
        ruff_res = subprocess.run(['ruff', 'check', temp_file], capture_output=True, text=True, timeout=30)
        mypy_res = None
        if file_path.endswith('.py'):
            mypy_res = subprocess.run(['mypy', temp_file], capture_output=True, text=True, timeout=30)

        return {
            "ruff": {"success": ruff_res.returncode == 0, "output": ruff_res.stdout + ruff_res.stderr},
            "mypy": {"success": (mypy_res.returncode == 0) if mypy_res else True,
                     "output": (mypy_res.stdout + mypy_res.stderr) if mypy_res else ""}
        }
    except subprocess.TimeoutExpired:
        logger.warning("linter_timeout")
        return {"ruff": {"success": False, "output": "Timeout"}, "mypy": {"success": False, "output": "Timeout"}}
    except Exception as e:
        logger.error("linter_error", extra={"error": str(e)})
        return {"ruff": {"success": False, "output": str(e)}, "mypy": {"success": False, "output": str(e)}}
    finally:
        try: os.unlink(temp_file)
        except: pass
```

---

Python: Automation Modules

cortex/automation/python_tests.py

```python
import os
import subprocess
import json
from typing import Dict, Any
from cortex.common.logging import get_logger

logger = get_logger(__name__)

class PythonTestAutomation:
    def run_pytest_with_coverage(self, test_path: str = "tests/") -> Dict[str, Any]:
        """Run pytest with coverage reporting"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", test_path, "--cov=.", "--cov-report=json", "-v"],
                capture_output=True, text=True, timeout=300,
            )
            coverage = None
            if os.path.exists("coverage.json"):
                try:
                    with open("coverage.json", "r", encoding="utf-8") as f:
                        coverage_data = json.load(f)
                        coverage = coverage_data.get("totals", {}).get("percent_covered")
                finally:
                    try: os.remove("coverage.json")
                    except: pass
            return {"success": result.returncode == 0, "output": result.stdout + result.stderr, "coverage": coverage}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Test execution timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def format_and_lint(self) -> Dict[str, Any]:
        """Run Black formatting and Ruff linting (with fixes)"""
        results = {}
        fmt = subprocess.run(["black", "."], capture_output=True, text=True)
        results["formatting"] = {"success": fmt.returncode == 0, "output": fmt.stdout + fmt.stderr}
        lint = subprocess.run(["ruff", "check", "--fix", "."], capture_output=True, text=True)
        results["linting"] = {"success": lint.returncode == 0, "output": lint.stdout + lint.stderr}
        return results
```

cortex/automation/typescript_tests.py

```python
import subprocess
import os
from typing import Dict, Any

class ExtensionTestAutomation:
    def _ext_dir(self) -> str:
        here = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(here, "..", "..", "cortex-extension"))

    def run_extension_tests(self) -> Dict[str, Any]:
        """Run VS Code extension tests (expects npm test configured)"""
        try:
            result = subprocess.run(["npm", "test"], cwd=self._ext_dir(), capture_output=True, text=True, timeout=900)
            return {"success": result.returncode == 0, "output": result.stdout + result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Extension tests timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def build_extension(self) -> Dict[str, Any]:
        """Build the VS Code extension (npm run compile)"""
        try:
            result = subprocess.run(["npm", "run", "compile"], cwd=self._ext_dir(), capture_output=True, text=True, timeout=600)
            return {"success": result.returncode == 0, "output": result.stdout + result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

cortex/automation/git_workflow.py

```python
import subprocess
from typing import Dict, Any, List

class GitAutomation:
    def create_feature_branch(self, feature_name: str) -> Dict[str, Any]:
        branch = f"feature/{feature_name.replace(' ', '-').lower()}"
        res = subprocess.run(["git", "checkout", "-b", branch], capture_output=True, text=True)
        return {"success": res.returncode == 0, "branch": branch, "output": res.stdout + res.stderr}

    def auto_commit(self, message: str, files: List[str] | None = None) -> Dict[str, Any]:
        if files:
            for f in files:
                subprocess.run(["git", "add", f], capture_output=True)
        else:
            subprocess.run(["git", "add", "."], capture_output=True)
        res = subprocess.run(["git", "commit", "-m", f"feat: {message}"], capture_output=True, text=True)
        return {"success": res.returncode == 0, "output": res.stdout + res.stderr}
```

cortex/automation/deployment.py

```python
import os
import subprocess
from typing import Dict, Any

class DeploymentAutomation:
    def deploy_to_test(self) -> Dict[str, Any]:
        """Shell out to your test deployment script"""
        try:
            res = subprocess.run(["./deploy_test.sh"], capture_output=True, text=True, timeout=900)
            return {"success": res.returncode == 0, "output": res.stdout + res.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def package_extension(self) -> Dict[str, Any]:
        """Package VS Code extension for publishing (expects npm run package)"""
        ext_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "cortex-extension"))
        try:
            res = subprocess.run(["npm", "run", "package"], cwd=ext_dir, capture_output=True, text=True, timeout=600)
            return {"success": res.returncode == 0, "output": res.stdout + res.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

---

Python: Automation API Router

cortex/api/endpoints/automation.py

```python
from fastapi import APIRouter, Body
from typing import Optional, List
from cortex.automation.python_tests import PythonTestAutomation
from cortex.automation.typescript_tests import ExtensionTestAutomation
from cortex.automation.git_workflow import GitAutomation
from cortex.automation.deployment import DeploymentAutomation

router = APIRouter(prefix="/api/automation", tags=["automation"])

@router.post("/run-python-tests")
async def run_python_tests():
    return PythonTestAutomation().run_pytest_with_coverage()

@router.post("/format-and-lint")
async def format_and_lint():
    return PythonTestAutomation().format_and_lint()

@router.post("/run-extension-tests")
async def run_extension_tests():
    return ExtensionTestAutomation().run_extension_tests()

@router.post("/build-extension")
async def build_extension():
    return ExtensionTestAutomation().build_extension()

@router.post("/create-feature-branch/{feature_name}")
async def create_feature_branch(feature_name: str):
    return GitAutomation().create_feature_branch(feature_name)

@router.post("/auto-commit")
async def auto_commit(message: str = Body(..., embed=True), files: Optional[List[str]] = Body(default=None, embed=True)):
    return GitAutomation().auto_commit(message, files)

@router.post("/deploy-test")
async def deploy_test():
    return DeploymentAutomation().deploy_to_test()

@router.post("/package-extension")
async def package_extension():
    return DeploymentAutomation().package_extension()
```

---

VS Code Extension

cortex-extension/tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "out",
    "rootDir": "src",
    "strict": true,
    "sourceMap": true,
    "esModuleInterop": true,
    "lib": ["ES2020"]
  },
  "include": ["src"]
}
```

cortex-extension/package.json

```json
{
  "name": "cortex-copilot-boost",
  "displayName": "Cortex Copilot Boost",
  "description": "Boost Copilot with repo-aware context, safe apply, and automation commands.",
  "version": "0.1.0",
  "publisher": "your-org",
  "engines": { "vscode": "^1.83.0" },
  "activationEvents": [
    "onCommand:cortex.boostSelection",
    "onCommand:cortex.applyGeneratedCode",
    "onCommand:cortex.runPythonTests",
    "onCommand:cortex.formatAndLint",
    "onCommand:cortex.buildExtension",
    "onView:cortex.situationBrief"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      { "command": "cortex.boostSelection", "title": "Cortex: Boost Selection", "category": "Cortex" },
      { "command": "cortex.applyGeneratedCode", "title": "Cortex: Apply Generated Code", "category": "Cortex" },
      { "command": "cortex.runPythonTests", "title": "Cortex: Run Python Tests", "category": "Cortex" },
      { "command": "cortex.formatAndLint", "title": "Cortex: Format & Lint (Python)", "category": "Cortex" },
      { "command": "cortex.buildExtension", "title": "Cortex: Build VS Code Extension", "category": "Cortex" }
    ],
    "viewsContainers": {
      "activitybar": [
        {
          "id": "cortex",
          "title": "Cortex",
          "icon": "resources/cortex.svg"
        }
      ]
    },
    "views": {
      "cortex": [
        { "id": "cortex.situationBrief", "name": "Situation Brief" }
      ]
    },
    "configuration": {
      "type": "object",
      "title": "Cortex",
      "properties": {
        "cortex.proxyUrl": {
          "type": "string",
          "default": "http://localhost:8000",
          "description": "Cortex proxy base URL"
        }
      }
    }
  },
  "scripts": {
    "compile": "tsc -p ./",
    "package": "vsce package"
  },
  "devDependencies": {
    "@types/node": "^20.4.2",
    "typescript": "^5.3.3",
    "vsce": "^2.15.0",
    "vscode": "^1.1.37"
  }
}
```

cortex-extension/src/commands/automation.ts

```typescript
import * as vscode from 'vscode';

const cfg = <T>(k: string, d: T) => vscode.workspace.getConfiguration('cortex').get<T>(k, d);
const post = async (url: string, body?: any) =>
  fetch(url, { method: 'POST', headers: {'Content-Type':'application/json'}, body: body ? JSON.stringify(body) : undefined })
  .then(async r => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status} ${await r.text()}`))));

export function registerAutomationCommands(ctx: vscode.ExtensionContext) {
  const base = cfg<string>('cortex.proxyUrl', 'http://localhost:8000');

  const runPy = vscode.commands.registerCommand('cortex.runPythonTests', async () => {
    try {
      const res = await post(`${base}/api/automation/run-python-tests`);
      vscode.window.showInformationMessage(res.success ? '✅ Python tests passed' : '❌ Python tests failed');
      if (res.output) showPanel('Python Tests', res.output);
    } catch (e: any) {
      vscode.window.showErrorMessage(`Run tests failed: ${e.message}`);
    }
  });

  const fmtLint = vscode.commands.registerCommand('cortex.formatAndLint', async () => {
    try {
      const res = await post(`${base}/api/automation/format-and-lint`);
      vscode.window.showInformationMessage('🧹 Format & Lint complete');
      if (res.formatting?.output || res.linting?.output) {
        showPanel('Format & Lint', `${res.formatting?.output ?? ''}\n${res.linting?.output ?? ''}`);
      }
    } catch (e: any) {
      vscode.window.showErrorMessage(`Format & Lint failed: ${e.message}`);
    }
  });

  const buildExt = vscode.commands.registerCommand('cortex.buildExtension', async () => {
    try {
      const res = await post(`${base}/api/automation/build-extension`);
      vscode.window.showInformationMessage(res.success ? '🛠️ Extension build completed' : '❌ Extension build failed');
      if (res.output) showPanel('Build Extension', res.output);
    } catch (e: any) {
      vscode.window.showErrorMessage(`Build extension failed: ${e.message}`);
    }
  });

  ctx.subscriptions.push(runPy, fmtLint, buildExt);
}

function showPanel(title: string, body: string) {
  const panel = vscode.window.createWebviewPanel('cortexPanel', title, vscode.ViewColumn.Beside, { enableScripts: false });
  panel.webview.html = `<html><body><pre>${body.replace(/[<>&]/g, (s)=>({ '<':'&lt;','>':'&gt;','&':'&amp;' } as any)[s])}</pre></body></html>`;
}
```

cortex-extension/src/extension.ts

```typescript
import * as vscode from 'vscode';
import * as path from 'path';
import { registerAutomationCommands } from './commands/automation';

function getConfig<T>(key: string, fallback: T): T {
  return vscode.workspace.getConfiguration('cortex').get<T>(key, fallback);
}

async function postJSON(url: string, body: any): Promise<any> {
  const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  return await res.json();
}

async function readSelectionOrDocument(): Promise<string> {
  const editor = vscode.window.activeTextEditor;
  if (!editor) return '';
  const sel = editor.selection;
  return sel && !sel.isEmpty ? editor.document.getText(sel) : editor.document.getText();
}

function showMarkdownDocument(title: string, content: string): Thenable<vscode.TextEditor> {
  return vscode.workspace.openTextDocument({ language: 'markdown', content }).then(doc => vscode.window.showTextDocument(doc, { preview: false }));
}

export function activate(context: vscode.ExtensionContext) {
  const proxyBase = getConfig<string>('proxyUrl', 'http://localhost:8000');

  // Cortex: Boost Selection
  const boostCommand = vscode.commands.registerCommand('cortex.boostSelection', async () => {
    try {
      const message = await readSelectionOrDocument();
      if (!message.trim()) {
        vscode.window.showWarningMessage('No text selected or document is empty.');
        return;
      }
      await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Cortex: Boosting prompt...',
        cancellable: false
      }, async (progress) => {
        progress.report({ increment: 50 });
        const payload = { message };
        const data = await postJSON(`${proxyBase}/v1/augment-prompt`, payload);
        const systemMessage = data.messages.find((m: any) => m.role === 'system')?.content || '';
        const userMessage = data.messages.find((m: any) => m.role === 'user')?.content || '';
        const markdownContent = `# 🚀 Cortex-Boosted Prompt

## System Message (Context)
\`\`\`
${systemMessage}
\`\`\`

## User Message (Your Prompt)
\`\`\`
${userMessage}
\`\`\`

> **Instructions**: Copy both sections above and paste into Copilot Chat.
`;
        progress.report({ increment: 100 });
        await showMarkdownDocument('Cortex Boosted Prompt', markdownContent);
      });
    } catch (error: any) {
      vscode.window.showErrorMessage(`Cortex Boost failed: ${error.message}`);
    }
  });

  // Cortex: Apply Generated Code
  const applyCommand = vscode.commands.registerCommand('cortex.applyGeneratedCode', async () => {
    try {
      const text = await readSelectionOrDocument();
      if (!text.trim()) {
        vscode.window.showWarningMessage('No text selected. Select Copilot response with code blocks.');
        return;
      }
      const payload = { response: text, original_prompt: 'N/A' };
      const result = await postJSON(`${proxyBase}/v1/process-response`, payload);
      const changes = result.changes as Array<{ file: string, content: string, description?: string, formatted: boolean, lint_passed: boolean }>;
      if (!changes.length) {
        vscode.window.showInformationMessage('No file changes found. Ensure code blocks start with "# file: path"');
        return;
      }

      const appliedFiles: string[] = [];
      let showTestResults = false;

      for (const change of changes) {
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '';
        const filePath = path.join(workspaceRoot, change.file);
        const fileUri = vscode.Uri.file(filePath);

        let currentContent = '';
        try {
          const fileData = await vscode.workspace.fs.readFile(fileUri);
          currentContent = Buffer.from(fileData).toString('utf8');
        } catch { currentContent = ''; }

        let previewContent = `# File: ${change.file}\n`;
        if (change.description) previewContent += `## Description: ${change.description}\n\n`;
        previewContent += `## Formatting Status: ${change.formatted ? '✅ Formatted' : '❌ Not Formatted'}\n`;
        previewContent += `## Linting Status: ${change.lint_passed ? '✅ Passed' : '❌ Failed'}\n\n`;
        previewContent += `## Current Content\n\`\`\`\n${currentContent || '[New File]'}\n\`\`\`\n\n`;
        previewContent += `## Proposed Changes\n\`\`\`\n${change.content}\n\`\`\``;

        const choice = await vscode.window.showQuickPick(['Apply Changes', 'Skip', 'Show Full Preview'],
          { placeHolder: `Apply changes to ${change.file}?` });

        if (choice === 'Show Full Preview') {
          await showMarkdownDocument(`Preview: ${change.file}`, previewContent);
          const confirmChoice = await vscode.window.showQuickPick(['Apply Changes', 'Skip'],
            { placeHolder: `Apply changes to ${change.file}?` });
          if (confirmChoice !== 'Apply Changes') continue;
        } else if (choice !== 'Apply Changes') {
          continue;
        }

        await vscode.workspace.fs.writeFile(fileUri, Buffer.from(change.content, 'utf8'));
        appliedFiles.push(change.file);
        showTestResults = true;
      }

      if (showTestResults && result.test_results) {
        const t = result.test_results as { passed: boolean, output: string, coverage?: number };
        const md = `# Test Results

## Status: ${t.passed ? '✅ PASSED' : '❌ FAILED'}
${t.coverage ? `## Coverage: ${t.coverage.toFixed(2)}%\n` : ''}

## Output
\`\`\`
${t.output}
\`\`\``;
        await showMarkdownDocument('Test Results', md);
      }

      if (appliedFiles.length > 0) {
        vscode.window.showInformationMessage(`Applied ${appliedFiles.length} file changes: ${appliedFiles.join(', ')}`);
      }
    } catch (error: any) {
      vscode.window.showErrorMessage(`Apply failed: ${error.message}`);
    }
  });

  // Situation Brief Webview
  class SituationBriefProvider implements vscode.WebviewViewProvider {
    public resolveWebviewView(webviewView: vscode.WebviewView): void {
      webviewView.webview.options = { enableScripts: true };
      const update = async () => {
        try {
          const data = await postJSON(`${proxyBase}/v1/augment-prompt`, { message: "Current situation brief" });
          const systemMessage = data.messages.find((m: any) => m.role === 'system')?.content || '';
          webviewView.webview.html = `<!DOCTYPE html>
<html><body>
  <div>✅ Connected to Cortex Proxy</div>
  <h3>🧠 Cortex Situation Brief</h3>
  <pre>${systemMessage.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
</body></html>`;
        } catch {
          webviewView.webview.html = `<!DOCTYPE html>
<html><body><div>❌ Disconnected from Cortex Proxy (${proxyBase})</div></body></html>`;
        }
      };
      update();
      const id = setInterval(update, 10000);
      webviewView.onDidDispose(() => clearInterval(id));
    }
  }

  const situationBriefProvider = new SituationBriefProvider();
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider('cortex.situationBrief', situationBriefProvider),
    boostCommand,
    applyCommand
  );

  // Register automation commands
  registerAutomationCommands(context);

  console.log('Cortex Copilot Boost extension activated');
}

export function deactivate() {}
```

---

That’s everything you need to run the proxy + extension and use the automation from a Codespace (or locally).

Happy building!
