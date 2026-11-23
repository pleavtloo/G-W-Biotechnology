import http.server, os, socketserver, sys

os.chdir(r"c:\Users\pleav\WorkBuddy AI\tl-de\dist")
handler = http.server.SimpleHTTPRequestHandler
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 8899), handler) as httpd:
    print("serving on http://127.0.0.1:8899", flush=True)
    httpd.serve_forever()
