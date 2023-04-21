import ipaddress
import sys

def mkcidr(df):
    if type(df) == str:
        ip_addr, subnet_mask = df.split()
        network_address = str(ipaddress.ip_network(f"{ip_addr}/{subnet_mask}", strict=False).network_address)
        cidr = str(ipaddress.ip_network(f"{ip_addr}/{subnet_mask}", strict=False).prefixlen)
        if int(cidr) == 32:
            addr = network_address
        else:
            addr = network_address + "/" + cidr

        return addr

def main(dfo):
    if type(dfo) == str:
        print(mkcidr(dfo))

if __name__ == "__main__":
    main(sys.argv[1])

