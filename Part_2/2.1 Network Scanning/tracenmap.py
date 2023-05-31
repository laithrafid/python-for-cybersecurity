import scapy.all as scapy

def traceroute(dst_ip):
  """Traces the route to a destination host.

  Args:
    dst_ip: The destination IP address.

  Returns:
    A list of hops in the route to the destination host.
  """

  hops = []
  progress = 0
  for ttl in range(1, 30):
    packet = scapy.IP(dst=dst_ip, ttl=ttl)
    response = scapy.sr1(packet)
    if response:
      hops.append(response.getlayer(scapy.IP).src)
      progress += 1
      print(f"{progress}/{len(hops)} hops completed...", end="\r")

  return hops

def check_open_ports(dst_ip, ports):
  """Checks the open ports on a destination host.

  Args:
    dst_ip: The destination IP address.
    ports: A list of ports to scan.

  Returns:
    A list of open ports on the destination host.
  """

  open_ports = []
  progress = 0
  for port in ports:
    packet = scapy.TCP(dst=dst_ip, dport=port)
    response = scapy.sr1(packet)
    if response and response.getlayer(scapy.TCP).flags == 'SA':
      open_ports.append(port)
      progress += 1
      print(f"{progress}/{len(ports)} ports scanned...", end="\r")

  return open_ports

def main():
  """The main function."""

  dst_ip = input('Enter the destination IP address: ')
  hops = traceroute(dst_ip)
  print('The route to the destination host is:')
  for hop in hops:
    print(hop)

  ports = [80, 443, 22]
  open_ports = check_open_ports(dst_ip, ports)
  print('The open ports on the destination host are:')
  for port in open_ports:
    print(port)

if __name__ == '__main__':
  main()
