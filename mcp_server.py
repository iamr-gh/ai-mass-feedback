import http.server
import socketserver
import json
import subprocess
import os

PORT = 8000

class MCPHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        prompt = data.get('prompt')

        if not prompt:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Prompt not provided'}).encode())
            return

        try:
            home_dir = os.path.expanduser("~")
            mcp_config_path = os.path.join(home_dir, ".mcp.json")
            with open(mcp_config_path, 'r') as f:
                mcp_config = json.load(f)

            mcp_servers = mcp_config.get("mcpServers", {})
            if not mcp_servers:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'No MCP servers found in ~/.mcp.json'}).encode())
                return

            # Assuming the first server is the one to use
            server_name = list(mcp_servers.keys())[0]
            server_info = mcp_servers[server_name]

            command = ["mcphost", "-m", "ollama:qwen2.5:7b-instruct","-p", prompt,"--quiet"]
            command[0] = os.path.expanduser(command[0])

            # Print input prompt to command line
            print("\n--- MCP INPUT ---")
            print(prompt)
            print("--- END INPUT ---\n", flush=True)

            # Start the process and do not send prompt to stdin (already passed as -p argument)
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Read stdout and stderr dynamically, print as it comes in
            import threading

            stdout_lines = []
            stderr_lines = []

            def read_stream(stream, lines, label):
                print(f"--- MCP {label} ---", flush=True)
                for line in iter(stream.readline, ''):
                    print(line, end='', flush=True)
                    lines.append(line)
                print(f"--- END {label} ---\n", flush=True)
                stream.close()

            stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, stdout_lines, "OUTPUT"))
            stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, stderr_lines, "STDERR"))
            stdout_thread.start()
            stderr_thread.start()
            stdout_thread.join()
            stderr_thread.join()
            returncode = process.wait()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'stdout': ''.join(stdout_lines),
                'stderr': ''.join(stderr_lines),
                'returncode': returncode
            }).encode())

        except FileNotFoundError:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'~/.mcp.json not found'}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

with socketserver.TCPServer(("", PORT), MCPHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()