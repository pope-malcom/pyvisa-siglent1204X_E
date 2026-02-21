import pyvisa
import time

# Set pyvisa-py as the backend - this should be the default though
pyvisa.ResourceManager('@py')

_rm = pyvisa.ResourceManager()

# IP address of the scope, may need to be configured
ipaddr = "TCPIP0::192.168.1.114::INSTR"

inst = _rm.open_resource(ipaddr)

# Increase timeout, which is necassary for the long reset operation
inst.timeout = 30000

# Reset the instrument
inst.write("*RST")
# Wait until operation complete
inst.query("*OPC?")

# Query instrument identity
print(inst.query("*IDN?"))
