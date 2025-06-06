# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automating the build, release, and Docker image publishing processes.

## Build and Release Workflow

The `build-and-release.yml` workflow automates the process of building the application for multiple platforms and creating a GitHub release with the binaries.

### How to use:

1. Go to the "Actions" tab in the GitHub repository
2. Select the "Build and Release" workflow
3. Click "Run workflow"
4. Enter the version number (e.g., `1.0.0`) and select whether it's a pre-release
5. Click "Run workflow"

The workflow will:
- Build the application for Windows, Linux, and macOS
- Create a GitHub release with the specified version
- Upload the binaries to the release
- Add release notes with download links

## Docker Build and Publish Workflow

The `docker-build-publish.yml` workflow automates the process of building and publishing Docker images to GitHub Container Registry (GHCR) for this project.

### Workflow Triggers

The workflow runs in the following scenarios:
- When a new release is published
- Manually via workflow dispatch (with an optional version parameter)

### What the Workflow Does

1. Checks out the repository code
2. Sets up .NET environment
3. Determines the version to use:
   - From the release tag if triggered by a release
   - From the input parameter if manually triggered
   - From the latest release if no version is specified
4. Downloads the Linux binary from the corresponding release
5. Builds the Docker image using the Dockerfile in the Docker directory
6. Pushes the image to GitHub Container Registry with tags:
   - `latest`
   - The specific version number

### Using the Published Docker Image

The Docker image is published to:
```
ghcr.io/thetechnetwork/plex-show-subtitles-on-rewind:latest
ghcr.io/thetechnetwork/plex-show-subtitles-on-rewind:[version]
```

See the [Docker Instructions](../Docker/Docker%20Instructions.md) for details on how to use the image.

### Manual Workflow Trigger

To manually trigger this workflow:
1. Go to the "Actions" tab in the repository
2. Select "Build and Publish Docker Image" workflow
3. Click "Run workflow"
4. Optionally specify a version tag (without the 'v' prefix)
5. Click "Run workflow"

### Requirements

- The repository must have releases with Linux binaries available
- The workflow uses the `GITHUB_TOKEN` which is automatically provided by GitHub Actions