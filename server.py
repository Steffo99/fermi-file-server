import socketserver
import os
import socket
import pickle

class FileServerRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        files = list(os.walk("."))
        self.request.send(pickle.dumps(files))
        filename = str(self.request.recv(1024), encoding="utf8").strip("\n")
        if filename == "":
            self.request.close()
            return
        file_path = os.path.relpath(filename)
        if os.path.isfile(file_path):
            print(f"Serving {file_path}")
            with open(file_path, "rb") as file:
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0, 0)
                self.request.send(bytes(str(file_size), encoding="utf8") + b"\n")
                while file_size > 0:
                    self.request.send(file.read(256))
                    file_size -= 256
            self.request.shutdown(socket.SHUT_RDWR)
            self.request.close()
        else:
            self.request.send(b"NO\n")
            self.request.shutdown(socket.SHUT_RDWR)
            self.request.close()


with socketserver.ThreadingTCPServer(("0.0.0.0", 3001), FileServerRequestHandler) as ss:
    try:
        ss.serve_forever()
    except KeyboardInterrupt:
        pass
