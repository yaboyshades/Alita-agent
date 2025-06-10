"""
Prompt Templates for Alita Agent Framework.
These are placeholders for when you integrate a real LLM for code generation.
"""

class PromptTemplates:
    TOOL_GENERATION = """
    You are an expert Python developer. Write a complete, self-contained Python script to accomplish the following task.
    The script MUST read a single JSON object from stdin and print a single JSON object to stdout.

    TASK: {task_description}
    
    CONTEXT from web search:
    {search_context}

    Your script should be named {tool_name}.py and have a main execution block.
    Example Input JSON: {example_input}
    Example Output JSON: {example_output}

    Begin script:
    ```python
    #!/usr/bin/env python3
    import sys
    import json

    def execute(params: dict):
        # Your implementation here
        pass

    if __name__ == "__main__":
        input_params = json.load(sys.stdin)
        result = execute(input_params)
        print(json.dumps(result, indent=2))
    ```
    """
