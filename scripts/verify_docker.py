#!/usr/bin/env python3
"""
Script to verify Docker image for Plex-Show-Subtitles-On-Rewind
This script can be used to verify the Docker image programmatically.
"""

import os
import sys
import subprocess
import argparse
import time
import json
from pathlib import Path


class Colors:
    """Terminal colors for output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_colored(message, color):
    """Print a colored message"""
    print(f"{color}{message}{Colors.NC}")


def run_command(command, check=True, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        print_colored(f"Error running command: {' '.join(command)}", Colors.RED)
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_docker_running():
    """Check if Docker is running"""
    print_colored("Checking if Docker is running...", Colors.YELLOW)
    result = run_command(["docker", "info"], check=False)
    if result.returncode != 0:
        print_colored("Docker is not running. Starting Docker...", Colors.YELLOW)
        # Try to start Docker daemon
        run_command(["sudo", "dockerd", ">", "/tmp/docker.log", "2>&1", "&"], check=False, capture_output=False)
        print("Waiting for Docker to start...")
        time.sleep(5)
        
        # Check again
        result = run_command(["docker", "info"], check=False)
        if result.returncode != 0:
            print_colored("Failed to start Docker. Please start it manually.", Colors.RED)
            sys.exit(1)
    
    print_colored("Docker is running.", Colors.GREEN)


def pull_docker_image(image_name):
    """Pull the Docker image"""
    print_colored(f"Pulling Docker image: {image_name}", Colors.YELLOW)
    run_command(["docker", "pull", image_name])
    print_colored("Image pulled successfully.", Colors.GREEN)


def inspect_docker_image(image_name):
    """Inspect the Docker image and return details"""
    print_colored(f"Inspecting Docker image: {image_name}", Colors.YELLOW)
    result = run_command(["docker", "inspect", image_name])
    image_info = json.loads(result.stdout)
    
    if not image_info:
        print_colored("Failed to get image information.", Colors.RED)
        sys.exit(1)
    
    # Extract relevant information
    image_id = image_info[0]["Id"]
    created = image_info[0]["Created"]
    size = image_info[0]["Size"]
    
    print(f"Image ID: {image_id}")
    print(f"Created: {created}")
    print(f"Size: {size} bytes ({size / (1024*1024):.2f} MB)")
    
    # Check if the image has the expected labels
    labels = image_info[0].get("Config", {}).get("Labels", {})
    print("\nImage Labels:")
    for key, value in labels.items():
        print(f"  {key}: {value}")
    
    return image_info


def run_docker_container(image_name, container_name, config_dir):
    """Run the Docker container and return the container ID"""
    print_colored(f"Running Docker container from image: {image_name}", Colors.YELLOW)
    
    # Create config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    
    # Remove container if it already exists
    run_command(["docker", "rm", "-f", container_name], check=False)
    
    # Run the container
    result = run_command([
        "docker", "run", "-d",
        "--name", container_name,
        "-v", f"{config_dir}:/app/config",
        image_name,
        "-auth-device-name", "DockerTest"
    ])
    
    container_id = result.stdout.strip()
    print_colored(f"Container started with ID: {container_id}", Colors.GREEN)
    return container_id


def check_container_logs(container_name, timeout=10):
    """Check the container logs for errors"""
    print_colored(f"Checking container logs (waiting up to {timeout} seconds)...", Colors.YELLOW)
    
    # Wait for the container to start and generate some logs
    time.sleep(2)
    
    # Get the logs
    result = run_command(["docker", "logs", container_name])
    logs = result.stdout
    
    print_colored("Container logs:", Colors.BLUE)
    print(logs)
    
    # Check for common error patterns
    error_patterns = [
        "Error:", "Exception:", "Failed:", "Could not", "Unhandled exception"
    ]
    
    for pattern in error_patterns:
        if pattern in logs:
            print_colored(f"WARNING: Found potential error in logs: '{pattern}'", Colors.YELLOW)
    
    return logs


def cleanup(container_name, config_dir, keep_container=False):
    """Clean up resources"""
    if not keep_container:
        print_colored(f"Stopping and removing container: {container_name}", Colors.YELLOW)
        run_command(["docker", "stop", container_name], check=False)
        run_command(["docker", "rm", container_name], check=False)
    else:
        print_colored(f"Keeping container running: {container_name}", Colors.YELLOW)
    
    print_colored("Verification complete.", Colors.GREEN)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Verify Docker image for Plex-Show-Subtitles-On-Rewind")
    parser.add_argument("--version", default="latest", help="Version to verify (default: latest)")
    parser.add_argument("--image", help="Docker image name (default: ghcr.io/thetechnetwork/plex-show-subtitles-on-rewind:<version>)")
    parser.add_argument("--container-name", default="plex-subtitles-test", help="Container name (default: plex-subtitles-test)")
    parser.add_argument("--config-dir", default="./docker-test-config", help="Config directory (default: ./docker-test-config)")
    parser.add_argument("--keep-container", action="store_true", help="Keep the container running after verification")
    args = parser.parse_args()
    
    # Set the image name if not provided
    if not args.image:
        args.image = f"ghcr.io/thetechnetwork/plex-show-subtitles-on-rewind:{args.version}"
    
    print_colored(f"Verifying Docker image: {args.image}", Colors.YELLOW)
    
    # Make config_dir absolute
    args.config_dir = os.path.abspath(args.config_dir)
    
    try:
        # Check if Docker is running
        check_docker_running()
        
        # Pull the Docker image
        pull_docker_image(args.image)
        
        # Inspect the Docker image
        image_info = inspect_docker_image(args.image)
        
        # Run the Docker container
        container_id = run_docker_container(args.image, args.container_name, args.config_dir)
        
        # Check the container logs
        logs = check_container_logs(args.container_name)
        
        print_colored("\nDocker image verification successful!", Colors.GREEN)
        return 0
    except Exception as e:
        print_colored(f"Error during verification: {e}", Colors.RED)
        return 1
    finally:
        # Clean up
        cleanup(args.container_name, args.config_dir, args.keep_container)


if __name__ == "__main__":
    sys.exit(main())