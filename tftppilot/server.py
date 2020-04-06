#!/usr/bin/env python3

import argparse
import logging
import os
import re

import requests

from fbtftp.base_handler import BaseHandler
from fbtftp.base_handler import StringResponseData
from fbtftp.base_handler import ResponseData
from fbtftp.base_server import BaseServer


class FileResponseData(ResponseData):
    def __init__(self, root, path):
        fullpath = re.sub("/+", "/", "%s/%s" % (root, path))
        self._size = os.stat(fullpath).st_size
        self._reader = open(fullpath, "rb")

    def read(self, n):
        return self._reader.read(n)

    def size(self):
        return self._size

    def close(self):
        self._reader.close()


class RequestHandler(BaseHandler):
    def __init__(self, server_addr, peer, path, options, root, pxe_pilot_url, pxe_pilot_local, stats_callback):
        self._root = root
        self._pxe_pilot_url = pxe_pilot_url
        self._pxe_pilot_local = pxe_pilot_local
        super().__init__(server_addr, peer, path, options, stats_callback)

    def get_mac_address(self, ip_addr):
        lines = os.popen('arp -a')
        for line in lines:
            token = line.split()
            arp_ip_addr = token[1].replace("(", "").replace(")", "")
            if arp_ip_addr == ip_addr:
                return token[3]
        return None

    def get_bootloader_response(self):
        peer_ip = self._peer[0]
        peer_mac = self.get_mac_address(peer_ip)

        if peer_mac == None:
            logging.info("Peer MAC address not found for %s" % peer_ip)
            raise Exception()

        logging.error("Peer MAC address found for %s : %s" %
                      (peer_ip, peer_mac))

        r = requests.get("%s/v1/hosts?status=false" % self._pxe_pilot_url)

        if r.status_code != 200:
            logging.error("Unable to read host list from PXE Pilot")
            raise Exception()

        hosts = r.json()

        logging.debug("PXE Pilot hosts read : %r" % hosts)

        pxe_pilot_host = None
        for host in hosts:
            for mac in host['macAddresses']:
                if mac == peer_mac:
                    logging.debug("Pxe Pilot host found :: %r" % host)
                    pxe_pilot_host = host
                    break

        if pxe_pilot_host != None and pxe_pilot_host['configuration']['name'] == self._pxe_pilot_local:
            logging.info(
                "PXE Pilot config is '%s'. Returning empty response to peer host %s" % (self._pxe_pilot_local, peer_ip))
            return StringResponseData("")

        logging.info(
            "Returning static file %s to peer host %s" % (self._path, peer_ip))

        return FileResponseData(self._root, self._path)

    def get_bootloader_config_response(self):
        peer_ip = self._peer[0]
        peer_mac = self.get_mac_address(peer_ip)
        filename = "pxelinux.cfg/01-" + peer_mac.lower().replace(":", "-")

        logging.info(
            "Returning bootloader config file %s to peer host %s" % (filename, peer_ip))

        return FileResponseData(self._root, filename)

    def get_response_data(self):
        if self._path == 'boot.efi' or self._path == '/boot.efi':
            return self.get_bootloader_response()

        if self._path == 'grub/grub.cfg' or self._path == '/grub/grub.cfg':
            return self.get_bootloader_config_response()

        logging.info(
            "Returning static file %s to peer host %s" % (self._path, self._peer[0]))

        return FileResponseData(self._root, self._path)


class TftpServer(BaseServer):
    def __init__(
        self,
        address,
        port,
        retries,
        timeout,
        root,
        pxe_pilot_url,
        pxe_pilot_local,
        handler_stats_callback,
        server_stats_callback=None,
    ):
        self._root = root
        self._pxe_pilot_url = pxe_pilot_url
        self._pxe_pilot_local = pxe_pilot_local
        self._handler_stats_callback = handler_stats_callback
        super().__init__(address, port, retries, timeout, server_stats_callback)

    def get_handler(self, server_addr, peer, path, options):
        return RequestHandler(
            server_addr, peer, path, options, self._root, self._pxe_pilot_url, self._pxe_pilot_local, self._handler_stats_callback
        )


def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--bind", type=str, default="::", help="IP address to bind to")

    parser.add_argument(
        "--port", type=int, default=6969, help="port to bind to")

    parser.add_argument(
        "--pxe-pilot-url", type=str, help="PXE Pilot API base URL")

    parser.add_argument(
        "--pxe-pilot-local", type=str, default="local", help="PXE Pilot local boot configuration name")

    parser.add_argument(
        "--retries", type=int, default=5, help="number of per-packet retries"
    )
    parser.add_argument(
        "--timeout", type=int, default=2, help="timeout for packet retransmission (s)"
    )
    parser.add_argument(
        "--log", type=str, default="INFO", help="Logging level (INFO, ERROR, DEBUG)"
    )
    parser.add_argument(
        "--root", type=str, default="", help="root of the static filesystem"
    )
    return parser.parse_args()


def print_session_stats(stats):
    logging.debug("Stats: for %r requesting %r" % (stats.peer, stats.file_path))
    logging.debug("Error: %r" % stats.error)
    logging.debug("Time spent: %dms" % (stats.duration() * 1e3))
    logging.debug("Packets sent: %d" % stats.packets_sent)
    logging.debug("Packets ACKed: %d" % stats.packets_acked)
    logging.debug("Bytes sent: %d" % stats.bytes_sent)
    logging.debug("Options: %r" % stats.options)
    logging.debug("Blksize: %r" % stats.blksize)
    logging.debug("Retransmits: %d" % stats.retransmits)
    logging.debug("Server port: %d" % stats.server_addr[1])
    logging.debug("Client port: %d" % stats.peer[1])


def print_server_stats(stats):
    """
    Print server stats - see the ServerStats class
    """
    counters = stats.get_and_reset_all_counters()
    logging.debug("Server stats - every %d seconds" % stats.interval)
    if "process_count" in counters:
        logging.debug(
            "Number of spawned TFTP workers in stats time frame : %d"
            % counters["process_count"]
        )


def main():
    args = get_arguments()

    if args.log == "INFO":
        log_level = logging.INFO
    elif args.log == "ERROR":
        log_level = logging.ERROR
    elif args.log == "DEBUG":
        log_level = logging.DEBUG
    else:
        print("ERROR : Invalid log level")

    logging.getLogger().setLevel(log_level)

    logging.info("Starting TFTP server on %s:%s" % (args.bind, args.port))
    logging.info("TFTP root directory is %s" % args.root)

    server = TftpServer(
        args.bind,
        args.port,
        args.retries,
        args.timeout,
        args.root,
        args.pxe_pilot_url,
        args.pxe_pilot_local,
        print_session_stats,
        print_server_stats,
    )
    try:
        server.run()
    except KeyboardInterrupt:
        server.close()


if __name__ == "__main__":
    main()
