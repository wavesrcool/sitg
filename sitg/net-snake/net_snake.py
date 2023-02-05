#!/usr/bin/env python3

import sys
import socket
import getopt
import threading
import subprocess

# globals
listen = False
command = False
upload = False
execute = ''
target = ''
upload_dest = ''
port = 0


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # connect to target host
        client.connect((target, port))
        # ensure data received & send to client
        if len(buffer):
            client.send(buffer)

        # await response data
        while True:
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            buffer = input("")
            buffer += '\n'
            client.send(buffer)
    except:
        print("[*] Exception! Exiting.")
        client.close()


def server_loop():
    global target
    # listen on all interfaces if unspecified target
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(
            target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):
    command = command.rstrip()
    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    # ensure upload destintion is defined
    if len(upload_dest):
        # read bytes
        file_buffer = ""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        # write bytes
        try:
            file_descriptor = open(upload_dest, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            client_socket.send(
                f'Successfully saved file to {upload_dest}\r\n')
        except:
            client_socket.send(f'Failed to save file to {upload_dest}\r\n')

    # ensure execution command is defined
    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    if command:
        while True:
            client_socket.send("<SITG:#> ")
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            response = run_command(cmd_buffer)
            client_socket.send(response)


def manual():
    print('[sitg]:\tNet Snake.')
    print('\tUsage: net_snake.py -t target_host -p port\n')
    print(
        '\t-l --listen                # listen on [host]:[port] for incoming connections')
    print('\t-e --execute=file_to_run   # execute the given file upon connection')
    print('\t-c --command               # initialize a command shell')
    print('\t-u --upload=destination    # write a file to desination upon connection\n\n')
    print('\tExamples:\n')
    print('\t- net_snake.py -t 192.168.0.1 -p 5555 -l -c')
    print('\t- net_snake.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe')
    print('\t- net_snake.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"')
    print('\t- echo \"HELLO\" | ./net_snake.py - t 192.168.11.12 - p 135')
    print('')
    sys.exit(0)


def main():
    global listen
    global command

    global execute
    global target
    global upload_dest

    global port

    if not len(sys.argv[1:]):
        manual()

    # read args
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", [
                                   "help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        manual()

    for o, a in opts:
        if o in ("-h", "--help"):
            manual()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_dest = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)
    if listen:
        server_loop()


main()
