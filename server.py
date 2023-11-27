import socket
import random
import re
import logging
import argparse



# Setting up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
DELIMITER = b'\n'  # Define a packet delimiter

def should_drop_packet(loss_rate):
    """ Determine whether to drop a packet based on the loss rate. """
    return random.random() < loss_rate


def handle_client(client_socket, loss_rate):
    highest_consecutive_packet = -1
    received_packets = set()
    buffer = b''
    ack_needed = False

    try:
        while True:
            try:
                data = client_socket.recv(1024)
                if not data: break  # Connection closed by client
                buffer += data

                # Handling Partial Packets
                while DELIMITER in buffer:
                    packet, buffer = buffer.split(DELIMITER, 1)
                    match = re.match(rb'Packet (\d+)', packet)
                    if not match:
                        logging.error(f"Error parsing packet data: {packet}")
                        continue

                    packet_num = int(match.group(1))
                    if should_drop_packet(loss_rate):
                        logging.info(f"Dropping packet {packet_num}")
                    else:
                        # Update received packets set
                        received_packets.add(packet_num)

                    if not highest_consecutive_packet + 1 in received_packets:
                        ack_message = f"ACK {highest_consecutive_packet}"
                        client_socket.sendall(ack_message.encode() + DELIMITER)
                        logging.info(f"Sent ACK for packet {highest_consecutive_packet}")

                    # Determine the highest consecutive packet
                    while highest_consecutive_packet + 1 in received_packets:
                        highest_consecutive_packet += 1
                        ack_message = f"ACK {highest_consecutive_packet}"
                        client_socket.sendall(ack_message.encode() + DELIMITER)
                        logging.info(f"Sent ACK for packet {highest_consecutive_packet}")

            except socket.timeout:
                logging.warning("Socket timeout occurred.")
                break

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        client_socket.close()
        logging.info("Client socket closed.")



def start_server(host, port, loss_rate):
    """ Start the TCP server. """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen()
        logging.info(f"Server listening on {host}:{port}")

        while True:
            client_socket, _ = server_socket.accept()
            handle_client(client_socket, loss_rate)

    except Exception as e:
        logging.error(f"Server error: {e}")

    finally:
        server_socket.close()
        logging.info("Server socket closed.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP Server for congestion control simulation")
    parser.add_argument("--host", type=str, default="localhost", help="Host address")
    parser.add_argument("--port", type=int, default=12346, help="Port number")
    parser.add_argument("--loss_rate", type=float, default=0.1, help="Packet loss rate")
    args = parser.parse_args()

    start_server(args.host, args.port, args.loss_rate)
