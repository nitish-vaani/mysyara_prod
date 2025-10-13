import subprocess
import argparse
import json

def run_livekit_dispatch(metadata, contact_number, agent_name):
    """Run the LiveKit dispatch command with the provided inputs."""

    # print("Running LiveKit dispatch command...")
    # print(f"Metadata: {metadata}")
    # Ensure contact number has "+" prefix
    if not contact_number.startswith('+'):
        contact_number = '+' + contact_number
    
    command = [
        "lk",
        "dispatch",
        "create",
        "--new-room",
        "--agent-name",
        agent_name,
        "--metadata",
        json.dumps(metadata),
        "--api-key",
        "APIoLr2sRCRJWY5",
        "--api-secret",
        "yE3wUkoQxjWjhteMAed9ubm5mYg3iOfPT6qBQfffzgJC",
        "--url",
        "wss://setupforretell-hk7yl5xf.livekit.cloud",
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {"success": True, "output": result.stdout, "error": None}
    except subprocess.CalledProcessError as e:
        return {"success": False, "output": None, "error": e.stderr}

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='LiveKit Dispatch Tool')
    parser.add_argument('--name', required=True, help='Customer name')
    parser.add_argument('--contact', required=True, help='Contact number with country code')
    parser.add_argument('--agent', required=True, help='Agent name')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the dispatch command
    result = run_livekit_dispatch(args.name, args.contact, args.agent)
    
    if result["success"]:
        print("Command executed successfully!")
        print("Output:", result["output"])
    else:
        print("Error executing command:", result["error"])