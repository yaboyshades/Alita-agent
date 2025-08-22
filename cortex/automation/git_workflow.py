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
