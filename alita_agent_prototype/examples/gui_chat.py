#!/usr/bin/env python3
"""Simple GUI chat interface for the Alita Agent Framework."""
import asyncio
import sys
from pathlib import Path
import tkinter as tk

# Add project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alita_agent import ManagerAgent  # noqa: E402
from alita_agent.config.settings import AlitaConfig  # noqa: E402


class AlitaChatGUI:
    """Tkinter-based chat window for interacting with the agent."""

    def __init__(self, root: tk.Tk, agent: ManagerAgent) -> None:
        self.agent = agent
        self.root = root
        self.root.title("Alita Agent Chat")

        self.chat_log = tk.Text(self.root, state="disabled", width=80, height=20)
        self.chat_log.pack(padx=10, pady=10)

        entry_frame = tk.Frame(self.root)
        entry_frame.pack(padx=10, pady=(0, 10))

        self.entry = tk.Entry(entry_frame, width=70)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.send_message)

        send_btn = tk.Button(entry_frame, text="Send", command=self.send_message)
        send_btn.pack(side=tk.LEFT, padx=(5, 0))

        self.entry.focus()

    def append_chat(self, speaker: str, text: str) -> None:
        self.chat_log.configure(state="normal")
        self.chat_log.insert(tk.END, f"{speaker}: {text}\n")
        self.chat_log.configure(state="disabled")
        self.chat_log.see(tk.END)

    def send_message(self, event=None) -> None:
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self.entry.delete(0, tk.END)
        self.append_chat("You", user_text)
        self.append_chat("Alita", "Thinking...")
        try:
            result = asyncio.run(self.agent.process_task(user_text))
            if result.get("success"):
                reply = result.get("result")
            else:
                reply = f"Error: {result.get('error')}"
        except Exception as exc:
            reply = f"Unexpected error: {exc}"
        # Replace the placeholder "Thinking..." with the actual reply
        self.chat_log.configure(state="normal")
        self.chat_log.delete("end-2l", "end-1l")
        self.chat_log.configure(state="disabled")
        self.append_chat("Alita", str(reply))


def main() -> None:
    """Launch the GUI chat interface."""
    config = AlitaConfig()
    agent = ManagerAgent(config)
    root = tk.Tk()
    AlitaChatGUI(root, agent)
    root.mainloop()


if __name__ == "__main__":
    main()
