import socket
import json


with open('config.json', 'r') as f:
    config = json.load(f)

IP = config['server_ip']
PORT = 53


def get_domain(dns_message):
    '''
    get_domain returns domain in friendly form for human.
    '''
    state = 0
    expectedlenght = 0
    domainstring = ''
    domainparts = []
    x = 0
    
    for byte in dns_message:
        if state == 1:
            domainstring += chr(byte) 
            x += 1
            if x == expectedlenght:
                domainparts.append(domainstring)
                domainstring = ''
                state = 0
                x = 0
            if byte == 0:
                domainparts.append(domainstring)
                break
        else:
            state = 1
            expectedlenght = byte
        x += 0
        
    return '.'.join(domainparts[:-1])


def send_udp_message(message, address, port):
    '''
    send_udp_message sends a message to DNS server.
    '''
    server_address = (address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(message, server_address)
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    return data


def run_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    print(f'Server is running on {IP}:{PORT}.\nWaiting requests...')

    while True:
        try:
            message, addr = sock.recvfrom(512)
        except ConnectionResetError:
            continue 
        
        domain = get_domain(message[12:])
        print("Request:", message)

        if domain not in config['black_list']:
            response = send_udp_message(message, config['outside_dns_server'], 53)
            print("Response:", response)
            sock.sendto(response, addr)
        else: 
            sock.sendto(bytes(config['answer'], 'utf-8'), addr)
            print("Response:", config['answer'])


if __name__ == '__main__':
    run_server()
