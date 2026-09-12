"""Local static preview with byte-range support for browser video seeking."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re


class PreviewHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.byte_range = None
        requested = self.headers.get('Range', '')
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', requested)
        path = Path(self.translate_path(self.path))
        if not match or not path.is_file():
            return super().send_head()
        source = path.open('rb')
        size = path.stat().st_size
        first, last = match.groups()
        if not first and not last:
            source.close()
            return super().send_head()
        start = int(first) if first else max(0, size - int(last))
        end = min(int(last), size - 1) if first and last else size - 1
        if start > end or start >= size:
            source.close()
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return None
        self.byte_range = (start, end)
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Last-Modified', self.date_time_string(path.stat().st_mtime))
        self.end_headers()
        source.seek(start)
        return source

    def end_headers(self):
        self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()

    def copyfile(self, source, outputfile):
        try:
            if self.byte_range is None:
                return super().copyfile(source, outputfile)
            remaining = self.byte_range[1] - self.byte_range[0] + 1
            while remaining > 0:
                data = source.read(min(64 * 1024, remaining))
                if not data:
                    break
                outputfile.write(data)
                remaining -= len(data)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass  # Browsers cancel pending media requests when playback stops.


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    handler = partial(PreviewHandler, directory=str(root))
    with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
        print(f'HiFun preview: http://127.0.0.1:{args.port}/', flush=True)
        server.serve_forever()
