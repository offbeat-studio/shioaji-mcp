# Contributing to Shioaji MCP Server

Thank you for your interest in contributing to the Shioaji MCP Server! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** to your local machine
3. **Set up the development environment** as described in the README.md

## Development Environment Setup

```bash
# Clone your fork
git clone https://github.com/your-username/shioaji-mcp.git
cd shioaji-mcp

# Install development dependencies
uv sync --extra test --extra lint

# Set up environment variables
cp .env.example .env
# Edit .env and fill in your API credentials
```

## Development Workflow

1. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes** and ensure they follow the project's coding standards

3. **Write or update tests** for your changes

4. **Run tests** to ensure everything works:
   ```bash
   uv run pytest
   ```

5. **Check code quality**:
   ```bash
   uv run ruff check src/ tests/
   uv run ruff format src/ tests/
   ```

6. **Commit your changes** with a clear and descriptive commit message:
   ```bash
   git commit -m "Add feature: description of your feature"
   # or
   git commit -m "Fix: description of the bug you fixed"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** from your fork to the main repository

## Pull Request Guidelines

When submitting a pull request, please:

1. **Reference any related issues** in your PR description
2. **Describe your changes** in detail
3. **Include screenshots or examples** if applicable
4. **Update documentation** if necessary
5. **Ensure all tests pass** and code quality checks succeed
6. **Keep your PR focused** on a single topic to make review easier

## Testing

We use pytest for testing. Please ensure your code includes appropriate tests:

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/shioaji_mcp
```

## Code Style

We follow these coding standards:

1. Use **ruff** for linting and formatting
2. Follow **PEP 8** style guidelines
3. Use **type hints** where appropriate
4. Write **docstrings** for functions and classes
5. Keep **line length** to 88 characters or less

## Documentation

Please update documentation when making changes:

1. Update **docstrings** for modified functions and classes
2. Update the **README.md** if necessary
3. Update or create **examples** if applicable

## Working with Docker

For Docker-related changes:

```bash
# Build the Docker image
docker build -t shioaji-mcp-dev .

# Test the Docker image
docker run --rm -i --platform=linux/amd64 \
  -e SHIOAJI_API_KEY=test_key \
  -e SHIOAJI_SECRET_KEY=test_secret \
  shioaji-mcp-dev
```

## Releasing

For maintainers, to create a new release:

1. Update the version in `pyproject.toml`
2. Create a new tag:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
3. The GitHub Actions workflow will automatically build and publish the Docker image to GHCR

## Getting Help

If you need help with contributing, please:

1. Check the **documentation** and **examples**
2. Look for similar **issues** that might have been resolved
3. Open a new **issue** with a clear description of your problem

Thank you for contributing to the Shioaji MCP Server!
