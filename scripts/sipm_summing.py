# Script to collect data on SiPM channels
import pyvisa
import time
from datetime import datetime
import os
import pandas as pd

ipaddr = "TCPIP0::192.168.1.114::INSTR"

out_path = os.path.expanduser("~/waveform_records/")
file_label = "test"

runs = 10

# Place scope configuration instructions here
def scope_config(osc):
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


def main():
    print("[Connecting to scope...", end='', flush=True)
    _rm = pyvisa.ResourceManager()
    osc = _rm.open_resource(ipaddr)
    print("Connected]")


    # Setup resource
    osc.timeout = 30000
    osc.chunk_size = 20*1024*1024 # From siglent docs

    # Reset scope
    print("[Reseting scope........", end='', flush=True)
    osc.write("*RST")
    osc.query("*OPC?")
    print("Reset]")

    # Disable reply header
    osc.write("CHDR OFF")

    # Load channel configuration
    scope_config(osc)
    
    # Create directory to hold output data
    os.makedirs(out_path)
    
    print("Starting measurements")
    for run in range(1, runs+1):
        print("  Run " + str(run).zfill(4) + ":", end='', flush=True)

        # Set trigger
        osc.write("TRMD SINGLE")

        # Create dataframe to hold data
        waveforms_df = pd.DataFrame()

        # Wait for trigger
        print(" [Waiting for trig...", end='', flush=True)
        wait_for_trig(osc)
        print("Done]", end='', flush=True)
        print("[Reading waveform...", end='', flush=True)

        # Read waveforms and add to data frame
        for chan in ["C1", "C2", "C3", "C4"]:
            if osc.query(chan+":TRACE?").rstrip() == "ON":
                read_waveform(osc, chan, waveforms_df)

        # Populate time series
        samp_rate = float(osc.query("SARA?"))
        tdiv = float(osc.query("TDIV?"))
        time_series = []
        for idx in range(0, len(waveforms_df.index)):
            time_data = -(tdiv*14/2)+idx*(1/samp_rate)
            time_series.append(time_data)

        waveforms_df.insert(0, "Time", time_series)
    
        time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = "run_" + str(run).zfill(4)

        file_name = time_stamp + "-" + file_label + "-" + run_id

        waveforms_df.to_csv(out_path + file_name + ".csv")
        print("Done]")
    
    print("Finished, files located at " + out_path)

# Read a waveform from the scope, writing the data to a dataframe
def read_waveform(osc, chan, df):
    # Get voltage division and offset
    vdiv = float(osc.query(chan + ":VDIV?"))
    ofst = float(osc.query(chan + ":OFST?"))

    #Read the waveform from scope, removing header and \n\n
    osc.write(chan + ":WF? DAT2")
    recv = list(osc.read_raw())[16:]
    recv.pop()
    recv.pop()

    # Convert waveform to voltage values, as per siglent programming guide
    for idx in range(0,len(recv)):
        if recv[idx] > 127:
            recv[idx] -= 256
        recv[idx] = (recv[idx]*(vdiv/25))-ofst

    df[chan] = recv

    return


# Wait for scope to aquire a waveform
def wait_for_trig(osc):
    while (osc.query("SAST?").rstrip() != "Stop"):
        time.sleep(0.2)


if __name__=='__main__':
    main()
