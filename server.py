import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs
import cgi

PORT = 8080
DIRECTORY = "public"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/upload':
            try:
                # Parse the form data
                content_type = self.headers.get('content-type')
                if content_type and 'multipart/form-data' in content_type:
                    # Use cgi to parse the multipart form
                    form = cgi.FieldStorage(
                        fp=self.rfile,
                        headers=self.headers,
                        environ={
                            'REQUEST_METHOD': 'POST',
                            'CONTENT_TYPE': content_type,
                        }
                    )
                    
                    # Get the audio file
                    audio_item = form['audio']
                    if audio_item.filename:
                        # Generate filename
                        from datetime import datetime
                        filename = f"lecture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
                        file_path = os.path.join('recordings', filename)
                        
                        # Save file
                        with open(file_path, 'wb') as f:
                            f.write(audio_item.file.read())
                        
                        print(f"Saved: {filename}")
                        
                        # Send success response
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"status": "saved", "filename": filename}).encode())
                    else:
                        self.send_error(400, "No audio file found")
                else:
                    self.send_error(400, "Invalid content type")
            except Exception as e:
                print(f"Error: {e}")
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Endpoint not found")

    # Add CORS headers to all responses
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

# Create recordings directory if it doesn't exist
if not os.path.exists('recordings'):
    os.makedirs('recordings')

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f">>> Server running at http://localhost:{PORT}")
    httpd.serve_forever()