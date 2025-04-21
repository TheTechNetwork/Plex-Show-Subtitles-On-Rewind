#!/usr/bin/env python3
"""
Script to verify build assets for Plex-Show-Subtitles-On-Rewind
This script can be used to verify the build assets programmatically.
"""

import os
import sys
import subprocess
import platform
import argparse
import glob
import shutil
from pathlib import Path

# Configuration
DEFAULT_VERSION = "0.0.1-test"
PLATFORMS = ["win-x64", "linux-x64", "osx-x64"]
MIN_FILE_SIZE = 1000000  # 1MB minimum file size


class Colors:
    """Terminal colors for output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    NC = '\033[0m'  # No Color


def print_colored(message, color):
    """Print a colored message"""
    print(f"{color}{message}{Colors.NC}")


def find_repo_root():
    """Find the repository root directory"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print_colored("Error: Not a git repository", Colors.RED)
        sys.exit(1)


def find_executable(directory, platform):
    """Find the executable in the directory"""
    if platform == "win-x64":
        pattern = os.path.join(directory, "*.exe")
        files = glob.glob(pattern)
        return next((f for f in files if "RewindSubtitleDisplayerForPlex" in f), None)
    else:
        # For Linux and macOS, find executable files
        executables = []
        for root, _, files in os.walk(directory):
            for file in files:
                if "RewindSubtitleDisplayerForPlex" in file:
                    file_path = os.path.join(root, file)
                    if os.access(file_path, os.X_OK):
                        executables.append(file_path)
        return executables[0] if executables else None


def check_executable(file_path, platform_name):
    """Check if a file exists and is valid"""
    print(f"Checking {platform_name} executable: ", end="")
    
    if not os.path.isfile(file_path):
        print_colored("FAILED - File not found", Colors.RED)
        return False
    
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size < MIN_FILE_SIZE:
        print_colored(f"FAILED - File too small ({file_size} bytes)", Colors.RED)
        return False
    
    # For non-Windows executables, check if they're executable
    if platform_name != "win-x64" and not os.access(file_path, os.X_OK):
        print_colored("FAILED - File not executable", Colors.RED)
        return False
    
    print_colored("PASSED", Colors.GREEN)
    return True


def build_for_platform(platform_name, version, build_dir, assets_dir):
    """Build the application for a specific platform"""
    print_colored(f"\nBuilding for {platform_name}...", Colors.YELLOW)
    
    # Determine file extension
    ext = ".exe" if platform_name == "win-x64" else ""
    
    # Build the application
    try:
        subprocess.run([
            "dotnet", "publish",
            "-c", "Release",
            "-r", platform_name,
            "--self-contained", "true",
            "-p:PublishSingleFile=true",
            "-p:PublishTrimmed=true",
            f"-p:Version={version}"
        ], check=True)
    except subprocess.CalledProcessError:
        print_colored(f"ERROR: Build failed for {platform_name}", Colors.RED)
        return False
    
    # Find the executable
    publish_dir = os.path.join(build_dir, platform_name, "publish")
    executable = find_executable(publish_dir, platform_name)
    
    if not executable:
        print_colored(f"ERROR: Could not find executable for {platform_name}", Colors.RED)
        print("Contents of publish directory:")
        for item in os.listdir(publish_dir):
            print(f"  {item}")
        return False
    
    print(f"Found executable: {executable}")
    
    # Copy to release assets directory with proper name
    target_file = os.path.join(assets_dir, f"RewindSubtitleDisplayerForPlex_{version}_{platform_name}{ext}")
    shutil.copy2(executable, target_file)
    
    if platform_name != "win-x64":
        os.chmod(target_file, 0o755)  # Make executable
    
    # Verify the executable
    return check_executable(target_file, platform_name)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Verify build assets for Plex-Show-Subtitles-On-Rewind")
    parser.add_argument("--version", default=DEFAULT_VERSION, help=f"Version to build (default: {DEFAULT_VERSION})")
    parser.add_argument("--platforms", nargs="+", default=PLATFORMS, 
                        help=f"Platforms to build (default: {' '.join(PLATFORMS)})")
    args = parser.parse_args()
    
    repo_root = find_repo_root()
    build_dir = os.path.join(repo_root, "bin", "Release", "net9.0")
    assets_dir = os.path.join(repo_root, "release-assets")
    
    # Create release assets directory
    os.makedirs(assets_dir, exist_ok=True)
    
    print_colored(f"Verifying build assets for version {args.version}", Colors.YELLOW)
    
    success = True
    for platform_name in args.platforms:
        if platform_name not in PLATFORMS:
            print_colored(f"WARNING: Unknown platform {platform_name}", Colors.YELLOW)
        
        if not build_for_platform(platform_name, args.version, build_dir, assets_dir):
            success = False
    
    if success:
        print_colored("\nAll build assets verified successfully!", Colors.GREEN)
        print(f"Release assets are available in: {assets_dir}")
        for item in os.listdir(assets_dir):
            print(f"  {item}")
        return 0
    else:
        print_colored("\nVerification failed for one or more platforms", Colors.RED)
        return 1


if __name__ == "__main__":
    sys.exit(main())