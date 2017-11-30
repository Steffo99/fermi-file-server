import socket
import sys
import time
import pickle
import os

c = socket.socket()

address = sys.argv[1]
port = sys.argv[2]
filename = sys.argv[3] if len(sys.argv) > 3 else None

c.connect((address, int(port)))
files = pickle.loads(c.recv(4096))
if filename is None:
    separator = {
        "posix": "/",  # Linux
        "nt": "\\",  # Windows
        "java": "/"  # MacOS
    }
    for directory in files:
        for file in directory[2]:
            print(f"{directory[0]}{separator[os.name]}{file}")
    c.close()
    sys.exit(2)

c.send(bytes(filename, encoding="utf8"))

status = str(c.recv(256), encoding="utf8")
if status == "NO\n":
    print("No such file exists on the server.")
else:
    status = int(status)
    print("Download started.")

with open("download/" + filename, "w") as file:
    file.write("")

ts = time.time()
size = status
while status > 0:
    data = c.recv(256)
    with open("download/" + filename, "ab") as file:
        file.write(data)
    print("█", end="")
    status -= 256
download_time = time.time() - ts
print(f"\nDownload complete."
      f"Download time: {download_time}"
      f"Download size: {size}"
          f"Download speed: {size / download_time}")