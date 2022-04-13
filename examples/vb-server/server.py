import os
import random
import socket
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def read_data(path):
    lines = []
    with open(path) as fd:
        while True:
            line = fd.readline()
            if not line:
                break
            lines.append(line)

    return lines


def main():
    data = read_data(os.path.join(BASE_DIR, "data.txt"))
    data_len = len(data)

    host = "127.0.0.1"
    port = 2020

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))

        print("Listening on %s:%s" % ((host, port)))
        sock.listen(5)

        while True:
            conn, addr = sock.accept()
            print("Client connected: %s:%s" % addr)

            try:
                while True:
                    index = random.randrange(data_len)
                    conn.send(bytes(data[index], "utf-8"))
                    time.sleep(1)
            except Exception as e:
                print(e)
            finally:
                conn.close()


if __name__ == "__main__":
    main()
