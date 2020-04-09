# TFTP Pilot

[![Build Status](https://travis-ci.com/ggiamarchi/tftp-pilot.svg?branch=master)](https://travis-ci.com/ggiamarchi/tftp-pilot)

TFTP Pilot is a dynamic TFTP server implementation to integrate with PXE Pilot.

It is based on the [fbtftp](https://github.com/facebook/fbtftp) framework.

## Quickstart

Installing TFTP Pilot is straightforward

```
pip3 install tftp-pilot
```

**Note.** It is tested with python 3 only.

Then, configuration is done through the command line only when running TFTP Pilot

```
python3 -m tftppilot.server --bind 172.16.99.1 --root /var/tftp --port 69 --pxe-pilot-url http://localhost:3478
```

## License

Everything in this repository is published under the MIT license.
