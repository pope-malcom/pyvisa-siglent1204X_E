# Script to collect data on SiPM channels
import pyvisa
import time
import matplotlib.pyplot as pl

ipaddr = "TCPIP0::192.168.1.114::INSTR"

def main():
    _rm = pyvisa.ResourceManager()
    osc = _rm.open_resource(ipaddr)

    # Setup resource
    osc.timeout = 30000
    osc.chunk_size = 20*1024*1024 # From siglent docs

    # Reset scope
    osc.write("*RST")
    osc.query("*OPC?")

    # Disable reply header
    osc.write("CHDR OFF")

    # Configure timebase
    osc.write("TDIV 500uS")

    # Configure channels
    osc.write("C1:TRACE ON")
    osc.write("C1:VDIV 1V")
    
    osc.write("C2:TRACE ON")
    osc.write("C2:VDIV 20mV")
    
    # Configure trigger
    osc.write("TRSE EDGE,SR,C2,HT,OFF")
    osc.write("C2:TRLV 32mV")
    osc.write("TRMD SINGLE")
    osc.query("INR?") # Reset state register


    # Wait for trigger
    wait_for_trig(osc)
    c1_wf = read_waveform("C1", osc)
    c2_wf = read_waveform("C2", osc)

    # Populate time series
    samp_rate = float(osc.query("SARA?"))
    tdiv = float(osc.query("TDIV?"))
    time_series = []
    for idx in range(0, len(c1_wf)):
        time_data = -(tdiv*14/2)+idx*(1/samp_rate)
        time_series.append(time_data)


    # Plot waveforms
    pl.figure(figsize=(7,5))
    pl.ylim(-5,5)
    pl.plot(time_series, c1_wf, markersize=2, label=u"Y-T")
    pl.plot(time_series, c2_wf, markersize=2, label=u"Y-T")
    pl.grid()
    pl.show()



def read_waveform(chan, osc):
    # Get voltage division and offset
    vdiv = float(osc.query(chan + ":VDIV?"))
    ofst = float(osc.query(chan + ":OFST?"))

    osc.write(chan + ":WF? DAT2")
    
    #Read the waveform from scope, removing header and \n\n
    recv = list(osc.read_raw())[16:]
    recv.pop()
    recv.pop()

    #Convert waveform to voltage values, as per siglent programming guide
    for idx in range(0,len(recv)):
        if recv[idx] > 127:
            recv[idx] -= 256
        recv[idx] = (recv[idx]*(vdiv/25))-ofst

    return recv


# Wait for scope to aquire a waveform
def wait_for_trig(osc):
    print("Waiting for trigger...", end='')
    while (osc.query("SAST?").rstrip() != "Stop"):
        time.sleep(0.2)
    print("Triggered!")


if __name__=='__main__':
    main()
