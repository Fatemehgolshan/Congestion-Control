import socket
import time
import logging

# Define log file name
log_file_name = 'tcp_cubic_simulation.log'

# Set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file_name,
                    filemode='w')  # 'w' for write mode

DELIMITER = b'\n'  # Define a packet delimiter

def cubic_window_size(time_since_last_congestion_event, cwnd_last_max, w_max):
    C = 0.4  # Cubic scaling constant
    return C * ((time_since_last_congestion_event)**3) + w_max

def start_client(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Initialize all variables at the start
    estimated_rtt = 1  # Initial estimate
    dev_rtt = 0.5  # Initial deviation
    alpha = 0.125
    beta = 0.25
    timeout = 100  # Initial timeout period
    cwnd = 1  # Congestion Window, in MSS units
    ssthresh = 64  # Slow Start Threshold
    w_max = 10  # Maximum window size before last congestion event
    cwnd_last_max = cwnd
    time_since_last_congestion_event = 0
    min_cwnd = 1  # Minimum congestion window size
    max_packets = 100  # Total number of packets to send
    packet_number = 0
    unacknowledged_packets = set()
    send_times = {}

    try:
        client_socket.connect((host, port))
        logging.info("Connected to server.")
    except Exception as e:
        logging.error(f"Error connecting to server: {e}")
        return

    try:
        while packet_number < max_packets:
            window_packets = min(cwnd, max_packets - packet_number)

            for _ in range(int(window_packets)):
                message = f"Packet {packet_number}"
                encode_message = message.encode() + DELIMITER
                client_socket.sendall(encode_message)
                send_times[packet_number] = time.time()
                unacknowledged_packets.add(packet_number)
                logging.info(f"Sent: {message}")
                packet_number += 1

            acks_received = 0
            duplicate_acks = 0
            last_ack = -1

            while acks_received < window_packets:
                client_socket.settimeout(timeout)
                ack_data = client_socket.recv(1024).decode()

                ack_messages = ack_data.split('ACK ')[1:]
                for ack_msg in ack_messages:
                    ack_msg = 'ACK ' + ack_msg.strip()
                    ack_parts = ack_msg.split()

                    if len(ack_parts) == 2 and ack_parts[0] == 'ACK':
                        ack_number = int(ack_parts[1])
                        receive_time = time.time()

                        if ack_number in unacknowledged_packets:
                            unacknowledged_packets.remove(ack_number)
                            acks_received += 1
                            logging.info(f"ACK received for packet {ack_number}")

                            send_time = send_times.get(ack_number)
                            if send_time:
                                sample_rtt = receive_time - send_time
                                estimated_rtt = (1 - alpha) * estimated_rtt + alpha * sample_rtt
                                dev_rtt = (1 - beta) * dev_rtt + beta * abs(sample_rtt - estimated_rtt)
                                timeout = estimated_rtt + 4 * dev_rtt
                                logging.debug(f"Sample RTT: {sample_rtt} seconds, Estimated RTT: {estimated_rtt} seconds, Dev RTT: {dev_rtt} seconds, Timeout Interval: {timeout} seconds")

                        if ack_number == last_ack:
                            duplicate_acks += 1
                            if duplicate_acks == 3:
                                logging.warning("Triple duplicate ACKs received. Fast Retransmit and Fast Recovery triggered.")
                                w_max = cwnd
                                cwnd_last_max = max(min_cwnd, cwnd)
                                ssthresh = max(min_cwnd, cwnd // 2)
                                cwnd = ssthresh + 3
                                time_since_last_congestion_event = 0
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
                            cwnd *= 2  # Slow start phase
                        else:
                            time_since_last_congestion_event += 1
                            cwnd = int(max(min_cwnd, cubic_window_size(time_since_last_congestion_event, cwnd_last_max, w_max)))
                            logging.debug(f"Time since last congestion event: {time_since_last_congestion_event}, CWND updated to {cwnd}")

    except socket.timeout:
        logging.warning("Timeout occurred. Retransmitting and adjusting congestion window.")
        w_max = cwnd
        cwnd_last_max = max(min_cwnd, cwnd)
        ssthresh = max(min_cwnd, cwnd // 2)
        cwnd = max(min_cwnd, cwnd // 2)
        time_since_last_congestion_event = 0
        if unacknowledged_packets:
            earliest_packet = min(unacknowledged_packets)
            retransmit_message = f"Packet {earliest_packet}"
            client_socket.sendall(retransmit_message.encode() + DELIMITER)
            send_times[earliest_packet] = time.time()
            logging.info(f"Retransmitted: {retransmit_message}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        client_socket.close()
        logging.info("Socket closed.")

if __name__ == "__main__":
    server_ip = '127.0.0.1'
    server_port = 12346
    start_client(host=server_ip, port=server_port)


