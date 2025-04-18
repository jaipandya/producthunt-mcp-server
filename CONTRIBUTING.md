# Contributing to Product Hunt MCP Server

Thank you for your interest in contributing! 🎉

## Getting Started

1. **Fork the repository** and clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/producthunt-mcp-server.git
   cd producthunt-mcp-server
   ```
2. **Install dependencies** (recommended: use a virtual environment):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```
   Or, with [uv](https://github.com/astral-sh/uv):
   ```bash
   pip install uv
   uv pip install -e .[dev]
   ```

## Code Style & Linting

- Follow [PEP8](https://peps.python.org/pep-0008/).
- Use [ruff](https://github.com/charliermarsh/ruff) for linting:
  ```bash
  ruff check .
  ```

## Making Changes

- Make your changes in a new branch:
  ```bash
  git checkout -b my-feature
  ```
- Ensure your code passes linting and tests before submitting a PR.
- Update documentation and the [CHANGELOG.md](./CHANGELOG.md) if needed.

## Submitting Pull Requests

- Open a pull request against the `main` branch.
- Fill out the PR description and describe your changes clearly.
- Reference any related issues.

## Reporting Issues

- Use [GitHub Issues](https://github.com/jaipandya/producthunt-mcp-server/issues) for bugs, feature requests, or questions.
- Please provide as much detail as possible (logs, steps to reproduce, etc.).

## Code of Conduct

- Be respectful and inclusive. See [Contributor Covenant](https://www.contributor-covenant.org/) for guidelines.

---

Thank you for helping make Product Hunt MCP Server better! 🚀 