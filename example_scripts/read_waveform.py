import pyvisa
import matplotlib.pyplot as pl

ipaddr = "TCPIP0::192.168.1.114::INSTR"

def main():
    _rm = pyvisa.ResourceManager()
    sds = _rm.open_resource(ipaddr)

    sds.write("CHDR OFF") # Disable header on response
    vdiv = sds.query("C1:VDIV?")
    ofst = sds.query("C1:OFST?")
    tdiv = sds.query("TDIV?")
    sara = sds.query("SARA?") # SAmple RAte
    
    # If sample rate is reported with SI prefix, remove it
    sara_unit = {'G':1E9,'M':1E6,'k':1E3}
    for unit in sara_unit.keys():
        if sara.find(unit)!=-1:
            sara = sara.split(unit)
            sara = float(sara[0])*sara_unit[unit]
            break
    sara = float(sara)

    # Set timeout and chunksize for large readout
    sds.timeout = 30000
    sds.chunk_size = 20*1024*1024


    ### Download waveform to PC
    # Write command to download waveform
    sds.write("C1:WF? DAT2")
    # Read raw binary data, convert to list, remove first 16 elements (header)
    # Format of header "DAT2,#9XXXXXXXXX", with X being length of block
    recv = list(sds.read_raw())[16:]

    # Remove the last two elements. This is "\n\n" - signifying the end of the block
    recv.pop()
    recv.pop()

    #Convert waveform data to voltage, as per programming guide
    volt_value = []

    for data in recv:
        if data > 127:
            data = data - 256
        else:
            pass
        volt_value.append(data)
   
    time_value = []
    for idx in range(0,len(volt_value)):
        volt_value[idx] = volt_value[idx]/25*float(vdiv)-float(ofst)
        time_data = -(float(tdiv)*14/2)+idx*(1/sara)
        time_value.append(time_data)
    
    # Plot waveform
    pl.figure(figsize=(7,5))
    pl.ylim(-5,5)
    pl.plot(time_value,volt_value,markersize=2,label=u"Y-T")
    pl.legend()
    pl.grid()
    pl.show()

if __name__=='__main__':
    main()
