#!/bin/bash
# Script to verify build assets for Plex-Show-Subtitles-On-Rewind

set -e

# Configuration
VERSION=${1:-"0.0.1-test"}
REPO_ROOT=$(git rev-parse --show-toplevel)
BUILD_DIR="$REPO_ROOT/bin/Release/net9.0"
RELEASE_ASSETS_DIR="$REPO_ROOT/release-assets"
PLATFORMS=("win-x64" "linux-x64" "osx-x64")

# Create release assets directory
mkdir -p "$RELEASE_ASSETS_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Verifying build assets for version $VERSION${NC}"

# Function to check if a file exists and is executable
check_executable() {
    local file=$1
    local platform=$2
    
    echo -n "Checking $platform executable: "
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}FAILED - File not found${NC}"
        return 1
    fi
    
    # Check file size
    local size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file")
    if [ "$size" -lt 1000000 ]; then
        echo -e "${RED}FAILED - File too small ($size bytes)${NC}"
        return 1
    fi
    
    # For non-Windows executables, check if they're executable
    if [[ "$platform" != "win-x64" ]]; then
        if [ ! -x "$file" ]; then
            echo -e "${RED}FAILED - File not executable${NC}"
            return 1
        fi
    fi
    
    echo -e "${GREEN}PASSED${NC}"
    return 0
}

# Function to find executable in a directory
find_executable() {
    local dir=$1
    local pattern=$2
    
    if [[ "$pattern" == *"win-x64"* ]]; then
        find "$dir" -type f -name "*.exe" | grep -i "RewindSubtitleDisplayerForPlex" | head -n 1
    else
        find "$dir" -type f -executable -name "RewindSubtitleDisplayerForPlex*" | head -n 1
    fi
}

# Build for each platform
for platform in "${PLATFORMS[@]}"; do
    echo -e "\n${YELLOW}Building for $platform...${NC}"
    
    # Determine file extension
    if [[ "$platform" == "win-x64" ]]; then
        ext=".exe"
    else
        ext=""
    fi
    
    # Build the application
    dotnet publish -c Release -r $platform --self-contained true -p:PublishSingleFile=true -p:PublishTrimmed=true -p:Version=$VERSION
    
    # Find the executable
    executable=$(find_executable "$BUILD_DIR/$platform/publish" "RewindSubtitleDisplayerForPlex")
    
    if [ -z "$executable" ]; then
        echo -e "${RED}ERROR: Could not find executable for $platform${NC}"
        echo "Contents of publish directory:"
        ls -la "$BUILD_DIR/$platform/publish"
        exit 1
    fi
    
    echo "Found executable: $executable"
    
    # Copy to release assets directory with proper name
    target_file="$RELEASE_ASSETS_DIR/RewindSubtitleDisplayerForPlex_${VERSION}_${platform}${ext}"
    cp "$executable" "$target_file"
    
    if [[ "$platform" != "win-x64" ]]; then
        chmod +x "$target_file"
    fi
    
    # Verify the executable
    check_executable "$target_file" "$platform" || exit 1
done

echo -e "\n${GREEN}All build assets verified successfully!${NC}"
echo -e "Release assets are available in: $RELEASE_ASSETS_DIR"
ls -la "$RELEASE_ASSETS_DIR"

exit 0