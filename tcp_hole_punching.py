import ipaddress
import random
import socket
import sys
import threading
import urllib.request
from typing import *


class ConnResult:
    def __init__(self) -> None:
        self.status: Optional[bool] = False
        self.result: Optional[tuple[socket.socket, tuple[str, int]]] = None
    
    def check(self):
        if self.status == True:
            return self.result
        return None



def create_conn(friend_addr: tuple[str, int], client: socket.socket):
    client.connect(friend_addr)  # this gonna block until... it accepted!


def acpt_conn(client: socket.socket, result: ConnResult):
    socket_to_friend, friend_addr = client.accept()  # this block until got a connection

    result.status = True
    result.result = (socket_to_friend, friend_addr)


def tcp_hole_punching(client_addr: tuple[str, int], friend_addr: tuple[str, int]):
    connecting_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connecting_socket.bind(client_addr)

    send_conn_req = threading.Thread(target=create_conn, args=(friend_addr, connecting_socket,), daemon=True)
    send_conn_req.start()

    send_conn_req.join(random.randint(0, 50) / 10)

    if send_conn_req.is_alive() == False:
        return connecting_socket
    else:
        try:
            connecting_socket.shutdown(socket.SHUT_WR)
            connecting_socket.close()
        except Exception as e:
            print("Boohoo 1", e)
            connecting_socket.close()

    del connecting_socket

    receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiving_socket.bind(client_addr)

    receiving_socket.listen(1)

    receiving_result = ConnResult()
    recv_conn_req = threading.Thread(target=acpt_conn, args=(receiving_socket, receiving_result,), daemon=True)

    recv_conn_req.start()

    recv_conn_req.join(30)

    if recv_conn_req.is_alive() == False:
        return receiving_result.result[0]
    else:
        try:
            receiving_socket.shutdown(socket.SHUT_WR)
            receiving_socket.close()
        except Exception as e:
            print("Boohoo 2", e)

    del receiving_socket

    # connecting_result = ConnResult()
    # receiving_result = ConnResult()
    # send_conn_req = threading.Thread(target=create_conn, args=(client_addr, friend_addr, connecting_result,), daemon=True)
    # recv_conn_req = threading.Thread(target=acpt_conn, args=(client_addr, receiving_result,), daemon=True)

    # send_conn_req.start()
    # recv_conn_req.start()

    # while True:
    #     sleep(5)

    #     if receiving_result.status == True:
    #         return receiving_result.result
    #     elif connecting_result.status == True:
    #         return connecting_result.result


def main():
    client_port = random.randint(10_000, 65_535)
    client_ip = socket.gethostbyname(socket.gethostname())
    client_addr = (client_ip, client_port)

    with urllib.request.urlopen("https://api.ipify.org/") as response:
        ip: str = response.read().decode()
    print(f"Your public ip is {ip}")
    print(f"Today we are running at port {client_addr[1]}\n")

    try:
        # verify by parsing
        friend_ip = f"{ipaddress.ip_address(input('Friend IP: ')):s}"
    except ValueError as e:
        print("Invalid IP, try again", e)
        sys.exit()

    try:
        friend_port = abs(int(input("Friend Port: ")))
        if friend_port > 65_535:
            raise ValueError
    except ValueError:
        print("Port must be an integer and less than or equal to 65,535")
        sys.exit()

    friend_addr = (friend_ip, friend_port)

    conn = tcp_hole_punching(client_addr, friend_addr)

    if isinstance(conn, socket.socket):
        print("We got a CONNECTION!")
    else:
        print("we didnt get anything")


if __name__ == "__main__":
    main()
