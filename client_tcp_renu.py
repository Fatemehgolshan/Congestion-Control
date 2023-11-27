import socket
import time
import logging

# Define log file name
log_file_name = 'tcp_reno_simulation.log'

# Set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file_name,
                    filemode='w')  # 'w' for write, 'a' for append

DELIMITER = b'\n'  # Define a packet delimiter

def start_client(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        logging.info("Connected to server.")

    except Exception as e:
        logging.error(f"Error connecting to server: {e}")
        return

    # Initialize RTT variables
    estimated_rtt = 1  # Initial estimate
    dev_rtt = 0.5  # Initial deviation
    alpha = 0.125
    beta = 0.25
    timeout = 100  # Initial timeout period

    cwnd = 1  # Congestion Window, in MSS (Maximum Segment Size) units
    ssthresh = 64  # Slow Start Threshold, in MSS
    max_packets = 100  # Total number of packets to send for this example

    packet_number = 0
    unacknowledged_packets = set()
    send_times = {}

    try:
        while packet_number < max_packets:
            window_packets = min(cwnd, max_packets - packet_number)

            # Sending packets as per congestion window
            for _ in range(int(window_packets)):
                message = f"Packet {packet_number}"
                try:
                    encode_message = message.encode() + DELIMITER
                    client_socket.sendall(encode_message)
                    send_times[packet_number] = time.time()
                    unacknowledged_packets.add(packet_number)  # Track sent packet
                    logging.info(f"Sent: {message}")
                except Exception as e:
                    logging.error(f"Error sending packet: {e}")
                    break

                packet_number += 1

            acks_received = 0
            duplicate_acks = 0
            last_ack = -1

            # Waiting for ACKs for sent packets
            while acks_received < window_packets:
                try:
                    logging.info(f'CWND:{cwnd} SSTHRESH:{ssthresh}')
                    client_socket.settimeout(timeout)
                    ack_data = client_socket.recv(1024).decode()

                    # Handling the possibility of receiving multiple ACKs at once
                    ack_messages = ack_data.split('ACK ')[1:]
                    for ack_msg in ack_messages:
                        ack_msg = 'ACK ' + ack_msg.strip()
                        ack_parts = ack_msg.split()

                        if len(ack_parts) == 2 and ack_parts[0] == 'ACK':
                            ack_number = int(ack_parts[1])
                            receive_time = time.time()

                            if ack_number in unacknowledged_packets:
                                # Validate that ACK is for a sent packet
                                unacknowledged_packets.remove(ack_number)
                                acks_received += 1
                                logging.info(f"ACK received for packet {ack_number}")

                                # Calculate SampleRTT
                                send_time = send_times.get(ack_number)
                                if send_time:
                                    sample_rtt = receive_time - send_time
                                    estimated_rtt = (1 - alpha) * estimated_rtt + alpha * sample_rtt
                                    dev_rtt = (1 - beta) * dev_rtt + beta * abs(sample_rtt - estimated_rtt)
                                    timeout = estimated_rtt + 4 * dev_rtt

                                    logging.debug(f"Estimated RTT: {estimated_rtt} seconds")
                                    logging.debug(f"Dev RTT: {dev_rtt} seconds")
                                    logging.debug(f"Timeout Interval: {timeout} seconds")

                            # Congestion control: ACK processing
                            if ack_number == last_ack:
                                duplicate_acks += 1
                                if duplicate_acks == 3:
                                    logging.warning("Triple duplicate ACKs received. Fast Retransmit and Fast Recovery triggered.")
                                    ssthresh = max(2, cwnd // 2)
                                    cwnd = ssthresh + 3
                                    logging.info(f'CWND:{cwnd} SSTHRESH:{ssthresh}')
                                    # Retransmit starting from the next packet after the last acknowledged packet
                                    for p in range(last_ack + 1, packet_number):
                                        if p in unacknowledged_packets:
                                            retransmit_message = f"Packet {p}"
                                            client_socket.sendall(retransmit_message.encode() + DELIMITER)
                                            send_times[p] = time.time()
                                            logging.info(f"Retransmitted: {retransmit_message}")
                                    break
                            else:
                                duplicate_acks = 0
                                last_ack = ack_number

                            if cwnd < ssthresh:
                                cwnd *= 2  # Exponential growth in slow start phase
                                logging.info(f"CWND doubled to {cwnd} in slow start phase.")

                            else:
                                cwnd += 1  # Linear growth in congestion avoidance phase
                                logging.info(f"CWND incremented to {cwnd} in congestion avoidance phase.")

                            logging.info(f'CWND:{cwnd} SSTHRESH:{ssthresh}')

                except socket.timeout:
                    logging.warning("Timeout occurred. Retransmitting and adjusting congestion window.")
                    ssthresh = max(2, cwnd // 2)
                    cwnd = 1
                    # Retransmit starting from the earliest unacknowledged packet
                    earliest_packet = min(unacknowledged_packets)
                    for p in range(earliest_packet, packet_number):
                        if p in unacknowledged_packets:
                            retransmit_message = f"Packet {p}"
                            client_socket.sendall(retransmit_message.encode() + DELIMITER)
                            send_times[p] = time.time()
                            logging.info(f"Retransmitted: {retransmit_message}")
                    break

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        client_socket.close()
        logging.info("Socket closed.")


if __name__ == "__main__":
    server_ip = '127.0.0.1'
    server_port = 12346
    print("Starting TCP Reno simulation client")
    start_client(host=server_ip, port=server_port)
