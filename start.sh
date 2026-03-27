#!/bin/bash
cd /Users/florian/Downloads/tracetour
exec python3 -c "
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
os.chdir('/Users/florian/Downloads/tracetour')
print('Serving on http://localhost:${1:-8000}', flush=True)
HTTPServer(('', ${1:-8000}), SimpleHTTPRequestHandler).serve_forever()
"
