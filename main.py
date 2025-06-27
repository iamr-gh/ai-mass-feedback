import subprocess

def run_mcphost(input_text):
    """
    Runs the mcphost command with the ollama:qwen2.5:7b-instruct model,
    pipes input_text to stdin, and returns the output from stdout.
    """
    cmd = [
        "~/go/bin/mcphost",
        "-m", "ollama:qwen2.5:7b-instruct"
    ]
    # Expand ~ to user home directory
    cmd[0] = subprocess.os.path.expanduser(cmd[0])

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        stdout, stderr = process.communicate(input=input_text, timeout=60)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        raise RuntimeError("mcphost command timed out")
    if process.returncode != 0:
        raise RuntimeError(f"mcphost failed: {stderr.strip()}")
    return stdout.strip()

# Example usage:
if __name__ == "__main__":
    user_input = input("Enter your prompt: ")
    output = run_mcphost(user_input)
    print("Output:\n", output)

