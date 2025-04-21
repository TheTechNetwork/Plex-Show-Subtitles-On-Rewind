# Build Verification Scripts

This directory contains scripts to verify the build assets and Docker images for Plex-Show-Subtitles-On-Rewind.

## Scripts

### 1. `verify-build.sh`

A bash script to build and verify the application for all platforms (Windows, Linux, macOS).

**Usage:**
```bash
./verify-build.sh [VERSION]
```

**Example:**
```bash
./verify-build.sh 1.0.0
```

### 2. `verify_build.py`

A Python script to build and verify the application for all platforms with more options.

**Usage:**
```bash
python3 verify_build.py [--version VERSION] [--platforms PLATFORM1 PLATFORM2 ...]
```

**Example:**
```bash
python3 verify_build.py --version 1.0.0 --platforms win-x64 linux-x64
```

### 3. `verify_docker.py`

A Python script to verify the Docker image.

**Usage:**
```bash
python3 verify_docker.py [--version VERSION] [--image IMAGE_NAME] [--container-name NAME] [--config-dir DIR] [--keep-container]
```

**Example:**
```bash
python3 verify_docker.py --version 1.0.0
```

## Verification Process

The verification scripts perform the following checks:

1. **Build Verification:**
   - Build the application for each platform
   - Find the executable in the build output
   - Check if the executable exists and has a reasonable file size
   - For non-Windows executables, check if they're executable
   - Copy the executables to a release assets directory

2. **Docker Verification:**
   - Check if Docker is running
   - Pull the Docker image
   - Inspect the Docker image for metadata
   - Run a container from the image
   - Check the container logs for errors
   - Clean up resources

## Integration with CI/CD

These scripts can be integrated into your CI/CD pipeline to verify the build assets before creating a release.

Example GitHub Actions workflow step:
```yaml
- name: Verify build assets
  run: |
    cd scripts
    python3 verify_build.py --version ${{ github.event.inputs.version }}
```

## Troubleshooting

If you encounter issues with the verification scripts:

1. Make sure you have the required dependencies installed:
   - .NET SDK
   - Docker (for Docker verification)
   - Python 3.6+

2. Check the build output for errors:
   - Look for compiler errors
   - Check if the executable is being generated in the expected location

3. For Docker verification issues:
   - Make sure Docker is running
   - Check if you have permission to pull from the container registry
   - Verify network connectivity