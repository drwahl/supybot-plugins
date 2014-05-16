#!/usr/bin/env python

try:
    import simplejson as json
except ImportError:
    import json
from httplib import HTTPSConnection

infoblox_host = 'infoblox.example.com'
username = 'user'
password = 'password'

def do_query(query):
    """executes webapi query"""

    conn = HTTPSConnection(infoblox_host)
    auth_header = 'Basic %s' % (':'.join([username, password]).encode('Base64').strip('\r\n'))
    conn.request(query[0], query[1], query[2], {'Authorization': auth_header, 'Content-Type': 'application/x-www-form-urlencoded'})
    result = json.loads(conn.getresponse().read())
    conn.close()
    return result


def host_query(host):
    """searches (substring matching) infoblox database for hostnames matching input (regex)"""

    results = do_query(('GET', '/wapi/v1.0/record:host', 'name~=%s' % host))

    hosts_and_ips = {}

    for host in results:
        hosts_and_ips[host['name']] = []
        ipaddrs = []
        for ips in host['ipv4addrs']:
            ipaddrs.append(ips['ipv4addr'])
        hosts_and_ips[host['name']] = ipaddrs

    return hosts_and_ips


def mac_query(mac):
    """searches infoblox database for hostnames/ips with matching input"""

    results = do_query(('GET', '/wapi/v1.0/lease', 'hardware~=%s' % mac))

    return results


def ip_query(ip):
    """searches (substring matching) infoblox database for hostnames with IPs matching input (regex)"""

    results = do_query(('GET', '/wapi/v1.0/record:host_ipv4addr', 'ipv4addr~=%s' % ip))

    ips_and_hosts = {}

    for host in results:
        ips_and_hosts[host['ipv4addr']] = []
        ips_and_hosts[host['ipv4addr']] = host['host']

    return ips_and_hosts


def vlan_query(ip):
    """determines vlan/network a given IP resides in"""

    network_results = do_query(('GET', '/wapi/v1.0/ipv4address', 'ip_address=%s' % ip))

    network = network_results[0]['network']
    results = do_query(('GET', '/wapi/v1.0/network', 'network=%s' % network))
    if type(results) is list:
        if len(results) is 1:
            results = results[0]

    return results
    
if __name__ == "__main__":

    import argparse

    cmd_parser = argparse.ArgumentParser(description='A simple interface for querying data from Infoblox')
    cmd_parser.add_argument('-H', '--host', dest='host_to_query', action='store', help='Host to query (substring parsing) for', required=False, default=False)
    cmd_parser.add_argument('-i', '--ip', dest='ip_to_query', action='store', help='IP to query (substring parsing) for', required=False, default=False)
    cmd_parser.add_argument('-v', '--vlan', dest='vlan_to_query', action='store', help='Report what VLAN an IP belongs in', required=False, default=False)
    cmd_parser.add_argument('-m', '--mac', dest='mac_to_query', action='store', help='Report what DHCP lease (IP) is associated with the given MAC address', required=False, default=False)
    args = cmd_parser.parse_args()

    if args.host_to_query:
        result = host_query(args.host_to_query)
        for host in result:
            print '%s: %s' % (host, ' '.join(result[host]))
    elif args.ip_to_query:
        result = ip_query(args.ip_to_query)
        for host in result:
            print '%s: %s' % (host, result[host])
    elif args.vlan_to_query:
        result = vlan_query(args.vlan_to_query)
        print '%s - %s' % (result['network'], result['comment'])
    elif args.mac_to_query:
        result = mac_query(args.mac_to_query)
        print result
    else:
        cmd_parser.print_help()
