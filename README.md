Siglent1204X-E remote interface scripts

Uses pyvisa and pyvisa-py backend to send SCPI commands to the oscilloscope. Currently this only works over TCP, the USB interface throws errors - suspect it's an issue with the laptop USB connection and not pyvisa.

For this to work, the oscilloscope must be connected to the PC with an ethernet cable. IP addresses may need to be added.
