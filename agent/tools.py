import math
import os
import subprocess
import tempfile

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

tavily = TavilySearch(api_key=os.getenv("TAVILY_API_KEY", ""))

# Tool 1 – Web Search
@tool
def web_search(query: str) -> str:
    """Search the web for current, real-time information using Tavily."""
    try:
        # search_depth="fast" helps keep things snappy 
        result = tavily.invoke({"query": query})
        
        # If it's a list (standard Tavily response), join the content
        if isinstance(result, list):
            return "\n\n".join([f"Source: {r.get('url')}\nContent: {r.get('content')}" for r in result])
        
        return str(result)
    except Exception as e:
        return f"Search error: {str(e)}"


# Tool 2 – Calculator
@tool
def calculator(expression: str) -> str:
    """Safely evaluate a mathematical expression.
    Supports arithmetic, trigonometry, logarithms, powers, etc.
    Examples: '2 ** 10', 'sqrt(144)', 'sin(pi / 2)', '(100 * 1.08) ** 5'
    Input: a valid Python math expression string."""
    try:
        safe_globals = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        safe_globals.update({
            "__builtins__": {},
            "abs": abs, "round": round,
            "min": min, "max": max,
            "sum": sum, "pow": pow,
        })
        result = eval(expression, safe_globals)  # noqa: S307
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero."
    except Exception as e:
        return f"Calculation error: {str(e)}"



# Tool 3 – Python Code Executor
@tool
def python_executor(code: str) -> str:
    """Execute a Python code snippet in a sandboxed subprocess and return its output.
    Useful for data processing, algorithms, string manipulation, etc.
    Has a 10-second execution timeout.
    Input: a valid Python code string."""
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(code)
            tmp_path = f.name

        import sys
        result = subprocess.run(
            [sys.executable, tmp_path],  # uses whatever python is running right now
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            return output if output else "Code executed successfully with no output."
        return f"Runtime error:\n{result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        return "Error: Execution timed out (10-second limit)."
    except Exception as e:
        return f"Executor error: {str(e)}"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)



# Tool 4 – File Reader
@tool
def file_reader(file_path: str) -> str:
    """Read and return contents of a local text-based file (.txt, .csv, .json, .md, .py, etc.).
    Returns the first 4000 characters if the file is large.
    Input: absolute or relative path to the file."""
    max_chars = 4000
    text_extensions = {
        ".txt", ".md", ".csv", ".json", ".py", ".js",
        ".html", ".css", ".yaml", ".yml", ".log",
        ".xml", ".toml", ".ini", ".env",
    }
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found at '{file_path}'."
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in text_extensions:
            return f"Error: Unsupported file type '{ext}'."
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        if len(content) > max_chars:
            return content[:max_chars] + f"\n\n... [truncated — {len(content)} total characters]"
        return content if content.strip() else "File is empty."
    except PermissionError:
        return f"Error: Permission denied reading '{file_path}'."
    except Exception as e:
        return f"File read error: {str(e)}"


# Exported list
tools = [web_search, calculator, python_executor, file_reader]