# GitHub Container Registry (GHCR) Guide

This document provides information on how to use the Shioaji MCP Docker images from GitHub Container Registry (GHCR) and how to manage the CI/CD process for maintainers.

## For Users

### Using Pre-built Docker Images

The Shioaji MCP server is available as a pre-built Docker image on GitHub Container Registry. This is the recommended way to use the server as it eliminates the need to build the image locally.

#### Available Tags

- `latest` - Latest stable release from the main branch
- `vX.Y.Z` (e.g., `v0.1.0`) - Specific version releases
- `dev` - Latest development build (may contain experimental features)

For production use, we recommend using a specific version tag.

#### Pulling the Image

```bash
# Pull the latest stable image
docker pull ghcr.io/musingfox/shioaji-mcp:latest

# Pull a specific version
docker pull ghcr.io/musingfox/shioaji-mcp:v0.1.0

# Pull the development version
docker pull ghcr.io/musingfox/shioaji-mcp:dev
```

#### Running the MCP Server

```bash
# Run with the latest stable image
docker run --rm -i --platform=linux/amd64 \
  -e SHIOAJI_API_KEY=your_api_key \
  -e SHIOAJI_SECRET_KEY=your_secret_key \
  ghcr.io/musingfox/shioaji-mcp:latest
```

### MCP Client Configuration

Add the following configuration to your MCP client:

```json
{
  "mcpServers": {
    "shioaji": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", "--platform=linux/amd64",
        "-e", "SHIOAJI_API_KEY=your_api_key",
        "-e", "SHIOAJI_SECRET_KEY=your_secret_key",
        "ghcr.io/musingfox/shioaji-mcp:latest"
      ]
    }
  }
}
```

## For Maintainers

### CI/CD Workflow

The project uses GitHub Actions to automatically build and publish Docker images to GitHub Container Registry. The workflow is defined in `.github/workflows/docker-publish.yml`.

#### Workflow Triggers

The CI/CD workflow is triggered by:

1. **Push to main branch**: Builds and publishes the `latest` tag
2. **Push to dev branch**: Builds and publishes the `dev` tag
3. **Creating a version tag** (e.g., `v0.1.0`): Builds and publishes version-specific tags
4. **Pull requests to main**: Builds the image but does not publish it

#### Versioning Strategy

The versioning strategy follows Semantic Versioning (SemVer):

- **Major version** (`X` in `vX.Y.Z`): Incompatible API changes
- **Minor version** (`Y` in `vX.Y.Z`): New features in a backward-compatible manner
- **Patch version** (`Z` in `vX.Y.Z`): Backward-compatible bug fixes

#### Creating a New Release

To create a new release:

1. Update the version in `pyproject.toml`
2. Create and push a new tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

This will trigger the workflow to build and publish the new version.

### Manual Publishing

If you need to manually publish a Docker image:

```bash
# Build the image
docker build -t ghcr.io/musingfox/shioaji-mcp:latest .

# Log in to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u musingfox --password-stdin

# Push the image
docker push ghcr.io/musingfox/shioaji-mcp:latest
```

### Troubleshooting

#### Permission Issues

If you encounter permission issues when pushing to GHCR:

1. Ensure your GitHub token has the `write:packages` scope
2. Verify that the repository has the correct visibility settings for packages

#### Failed Builds

If a build fails in the CI/CD pipeline:

1. Check the GitHub Actions logs for error messages
2. Verify that the Dockerfile is valid and all dependencies are accessible
3. Ensure the GitHub Actions runner has sufficient resources

## Security Considerations

### API Credentials

Never hardcode API credentials in your Docker images or configuration files. Always use environment variables or secure secrets management.

### Image Security

The Docker image is built with security in mind:

- Uses a non-root user (`appuser`)
- Minimizes the number of installed packages
- Removes build dependencies after installation
- Uses a specific Python version rather than `latest`

### Regular Updates

Keep your Docker images up to date to benefit from security patches and improvements:

```bash
docker pull ghcr.io/musingfox/shioaji-mcp:latest
```

## Additional Resources

- [GitHub Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
