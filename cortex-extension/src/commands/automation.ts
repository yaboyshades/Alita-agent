import * as vscode from 'vscode';

const cfg = <T>(k: string, d: T) => vscode.workspace.getConfiguration('cortex').get<T>(k, d);
// Helper to POST JSON and return the parsed body. We annotate the return type as
// `Promise<any>` so callers are free to access response properties without
// TypeScript flagging them as `unknown` when `strict` mode is enabled.
const post = async (url: string, body?: any): Promise<any> =>
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined
  }).then(async r => {
    if (!r.ok) throw new Error(`HTTP ${r.status} ${await r.text()}`);
    return r.json();
  });

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
