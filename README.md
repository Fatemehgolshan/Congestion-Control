# Congestion-Control


# TCP Congestion Control Project

## Overview
This project explores and simulates the behavior of two TCP congestion control algorithms: TCP Reno and CUBIC. The objective is to understand how each algorithm adjusts the size of the congestion window (CWND) and how it affects the overall network performance in terms of throughput, Round-Trip Time (RTT), and packet loss.

## TCP Reno
TCP Reno is one of the early congestion control algorithms implemented as part of the TCP/IP stack. It uses a combination of slow start, congestion avoidance, fast retransmit, and fast recovery mechanisms to dynamically adjust the size of the congestion window.

Key characteristics of TCP Reno:
- Slow Start: CWND increases exponentially until it reaches the slow start threshold (SSThresh).
- Congestion Avoidance: Above SSThresh, CWND increases linearly to probe for additional available bandwidth.
- Fast Retransmit and Recovery: Upon detecting packet loss via triple duplicate ACKs, TCP Reno performs a fast retransmit and reduces CWND to ssthresh/2, then transitions to congestion avoidance.

## CUBIC
CUBIC is a more recent congestion control algorithm designed for high bandwidth, high latency networks. It differs from Reno primarily in how it increases the CWND after a loss event.

Key characteristics of CUBIC:
- Window Growth: CWND follows a cubic function with respect to time since the last congestion event, allowing for rapid window growth.
- Fairness and Stability: CUBIC adjusts its concave and convex regions to achieve fairness with other flows and stability of the congestion window.
