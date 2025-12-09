# IDE Setup Guide

This document explains the IDE/editor configuration for the TruLedgr API project.

## Quick Start

### VS Code (Recommended)

1. **Install VS Code**: https://code.visualstudio.com/

2. **Open the project**:
   ```bash
   code /Users/nathan/Documents/API
   ```

3. **Install recommended extensions**:
   - VS Code will prompt you to install recommended extensions
   - Or press `Cmd+Shift+P` → "Extensions: Show Recommended Extensions"

4. **Select Python interpreter**:
   - Press `Cmd+Shift+P` → "Python: Select Interpreter"
   - Choose the Poetry virtual environment (`.venv/bin/python`)

5. **You're ready to code!**

## Configuration Files

### `.editorconfig`
Universal editor configuration that works across all editors (VS Code, PyCharm, Sublime, etc.).

**What it does**:
- Enforces consistent line endings (LF)
- Sets indentation (4 spaces for Python, 2 for YAML/JSON)
- Ensures UTF-8 encoding
- Trims trailing whitespace
- Adds final newline to files

**Supported by**: VS Code, PyCharm, IntelliJ, Sublime Text, Atom, etc.

### `.vscode/settings.json`
VS Code workspace settings.

**Key features**:
- **Python**: Pylance language server, type checking
- **Formatting**: Black with 79 character line length
- **Linting**: Ruff for fast Python linting
- **Testing**: Pytest integration
- **Auto-format**: Format on save enabled
- **Exclusions**: Hides `__pycache__`, `.pytest_cache`, etc.

### `.vscode/extensions.json`
Recommended VS Code extensions.

**Installed automatically**:
- Python & Pylance (Microsoft)
- Black Formatter
- Ruff Linter
- Pytest Support
- GitLens
- Markdown support
- Docker support
- And more...

### `.vscode/launch.json`
Debug configurations.

**Available debuggers**:
- **Python: FastAPI** - Debug the API server
- **Python: Current File** - Debug the active file
- **Python: Debug Tests** - Debug all tests in file
- **Python: Debug Current Test** - Debug selected test
- **Python: Attach to Docker** - Debug containerized app

### `.vscode/tasks.json`
Quick tasks accessible via `Cmd+Shift+B`.

**Available tasks**:
- Run Development Server (default build task)
- Run Tests (default test task)
- Run Tests with Coverage
- Format Code (Black)
- Lint Code (Ruff)
- Type Check (Mypy)
- Install/Update Dependencies
- Build/Serve Documentation
- Clean Cache

### `.vscode/snippets.code-snippets`
Custom code snippets for faster development.

**Available snippets** (type prefix + Tab):
- `route` - FastAPI route handler
- `pydmodel` - Pydantic model
- `dbdep` - Database provider dependency
- `filedep` - File provider dependency
- `atest` - Async test function
- `repomethod` - Repository method
- `service` - Service method
- `settings` - Settings class
- `exception` - Exception class
- `dataclass` - Python dataclass

## Using VS Code

### Running the Development Server

**Option 1: Debug mode**
1. Press `F5` or go to Run & Debug (Cmd+Shift+D)
2. Select "Python: FastAPI"
3. Set breakpoints in your code
4. Server runs at http://localhost:8000

**Option 2: Task**
1. Press `Cmd+Shift+B` (Build Task)
2. Select "Run Development Server"

**Option 3: Terminal**
```bash
poetry run uvicorn api.main:app --reload
```

### Running Tests

**Option 1: Test Explorer**
1. Click Testing icon in sidebar
2. Click "Configure Python Tests" → pytest
3. Select `tests` directory
4. Click ▶️ to run tests

**Option 2: Debug Test**
1. Open test file
2. Click "Debug Test" above test function
3. Or select test name and press F5 with "Debug Current Test"

**Option 3: Task**
1. Press `Cmd+Shift+P`
2. Type "Tasks: Run Test Task"
3. Select "Run Tests"

### Code Formatting

**Automatic** (on save):
- Files are automatically formatted when you save

**Manual**:
- Press `Shift+Alt+F` (Format Document)
- Or run task: "Format Code (Black)"

### Linting

**Automatic**:
- Errors/warnings appear as you type
- Powered by Ruff (very fast)

**Manual**:
- Run task: "Lint Code (Ruff)"

### Code Navigation

- **Go to Definition**: `F12` or Cmd+Click
- **Find References**: `Shift+F12`
- **Go to Symbol**: `Cmd+Shift+O`
- **Go to File**: `Cmd+P`
- **Command Palette**: `Cmd+Shift+P`

### Code Snippets

Type prefix and press `Tab`:

```python
# Type 'route' + Tab
@router.get("/path")
async def function_name() -> ResponseModel:
    """Description."""
    pass

# Type 'pydmodel' + Tab
class ModelName(BaseModel):
    """Description."""
    field: str = Field(..., description="Field description")

# Type 'atest' + Tab
@pytest.mark.asyncio
async def test_function_name():
    """Test description."""
    # Arrange
    # Act
    # Assert
    pass
```

## PyCharm / IntelliJ IDEA

### Initial Setup

1. **Open project**: File → Open → Select project directory

2. **Configure Python interpreter**:
   - Settings → Project → Python Interpreter
   - Add → Poetry Environment
   - Select existing environment: `.venv`

3. **Enable EditorConfig**:
   - Settings → Editor → Code Style
   - Check "Enable EditorConfig support"

### Configuration

PyCharm automatically detects:
- Poetry configuration (`pyproject.toml`)
- Pytest as test runner
- EditorConfig settings

**Recommended settings**:
- Settings → Tools → Python Integrated Tools
  - Default test runner: pytest
  - Docstring format: Google
- Settings → Editor → Code Style → Python
  - Use EditorConfig: ✓
  - Hard wrap at: 79

### Running & Debugging

**Run server**:
1. Create run configuration
2. Script path: `uvicorn`
3. Parameters: `api.main:app --reload`

**Run tests**:
- Right-click test file/function → Run
- Or use pytest tool window

## Other Editors

### Sublime Text
- Install Package Control
- Install "EditorConfig" package
- Install "Anaconda" for Python support
- Settings will be inherited from `.editorconfig`

### Vim / Neovim
- Install `editorconfig-vim` plugin
- Install Python LSP (e.g., coc-pyright)
- EditorConfig will automatically apply

### Emacs
- Install `editorconfig-emacs`
- Use `lsp-mode` with `lsp-pyright`

## Troubleshooting

### VS Code doesn't find Python interpreter

**Solution**:
```bash
# Ensure virtual environment exists
poetry install

# Select interpreter in VS Code
Cmd+Shift+P → "Python: Select Interpreter"
# Choose: .venv/bin/python
```

### Import errors in VS Code

**Solution 1**: Reload window
- `Cmd+Shift+P` → "Developer: Reload Window"

**Solution 2**: Check PYTHONPATH
- Settings should include: `"python.analysis.extraPaths": ["${workspaceFolder}"]`

**Solution 3**: Restart Pylance
- `Cmd+Shift+P` → "Pylance: Restart Server"

### Tests not discovered

**Solution**:
1. Delete `.pytest_cache/`
2. `Cmd+Shift+P` → "Python: Configure Tests"
3. Select pytest → tests directory
4. Reload window

### Formatting not working

**Solution**:
1. Ensure Black is installed: `poetry install --with dev`
2. Check formatter: `Cmd+Shift+P` → "Format Document With..."
3. Select "Black Formatter"
4. Enable format on save in settings

### Extensions not installing

**Solution**:
1. Check internet connection
2. Manually install: Extensions panel → Search by ID
3. Or: `code --install-extension ms-python.python`

## Team Collaboration

### Sharing Configuration

**Committed to Git** (shared with team):
- `.editorconfig` - Editor settings
- `.vscode/extensions.json` - Recommended extensions
- `.vscode/launch.json` - Debug configs
- `.vscode/tasks.json` - Build tasks
- `.vscode/snippets.code-snippets` - Code snippets

**Not committed** (personal preferences):
- `.vscode/settings.json` - Might have personal paths
- Local editor configs
- Personal keybindings

### For New Team Members

1. Clone repository
2. Run `poetry install`
3. Open in VS Code
4. Install recommended extensions
5. Start coding!

## Keyboard Shortcuts (VS Code)

### Essential

| Action | macOS | Windows/Linux |
|--------|-------|---------------|
| Command Palette | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| Quick Open File | `Cmd+P` | `Ctrl+P` |
| Toggle Terminal | `Ctrl+` ` | `Ctrl+` ` |
| Format Document | `Shift+Alt+F` | `Shift+Alt+F` |
| Go to Definition | `F12` | `F12` |
| Find References | `Shift+F12` | `Shift+F12` |
| Rename Symbol | `F2` | `F2` |
| Show Problems | `Cmd+Shift+M` | `Ctrl+Shift+M` |
| Run Debugger | `F5` | `F5` |
| Toggle Breakpoint | `F9` | `F9` |

### Custom Tasks

| Action | Shortcut |
|--------|----------|
| Run Build Task | `Cmd+Shift+B` |
| Run Test Task | No default (customize) |

## Best Practices

1. **Always use the Poetry environment** - Don't install packages globally
2. **Format on save** - Keep code consistently formatted
3. **Run tests frequently** - Use test explorer or debugger
4. **Use snippets** - Speed up common patterns
5. **Set breakpoints** - Debug instead of print statements
6. **Use type hints** - Get better autocomplete and error detection
7. **Check problems panel** - Address linting issues as you code

## Additional Resources

- [VS Code Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [EditorConfig Documentation](https://editorconfig.org/)
- [Black Code Style](https://black.readthedocs.io/)
- [Ruff Linter](https://docs.astral.sh/ruff/)
- [Pylance Features](https://github.com/microsoft/pylance-release)
