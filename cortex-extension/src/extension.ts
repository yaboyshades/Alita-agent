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
