import pyvisa
import time

pyvisa.ResourceManager('@py')

_rm = pyvisa.ResourceManager()

ipaddr = "TCPIP0::192.168.1.114::INSTR"

osc = _rm.open_resource(ipaddr)

osc.timeout = 30000
osc.chunk_size = 20*1024*1024

osc.write("*RST")
osc.query("*OPC?")
print(osc.query("*IDN?"))


file_name = "test.bmp"
osc.write("SCDP")
result_str = osc.read_raw()
f = open(file_name,'wb')
f.write(result_str)
f.flush()
f.close()
