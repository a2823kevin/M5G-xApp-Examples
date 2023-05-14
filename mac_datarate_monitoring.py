import xapp_sdk
import time

def bpsToMbps(dataRate):
    return dataRate /1e6

class MACCallback(xapp_sdk.mac_cb):
    def __init__(self):
        xapp_sdk.mac_cb.__init__(self)
        self.prev_tstamp = 0
        self.prev_ul_total_bytes = 0
        self.prev_dl_total_bytes = 0

    def handle(self, ind):
        if (len(ind.ue_stats)>0):
            for i in range(len(ind.ue_stats)):
                #Calculate the datarate by dividing the TX bytes by time difference between 2 indications
                ul_data_rate = (ind.ue_stats[i].ul_aggr_tbs-self.prev_ul_total_bytes) * 8 / (ind.tstamp-self.prev_tstamp)
                dl_data_rate = (ind.ue_stats[i].dl_aggr_tbs-self.prev_dl_total_bytes) * 8 / (ind.tstamp-self.prev_tstamp)
                if (ul_data_rate<=0 or dl_data_rate<=0):
                    return
                
                #print out the daterates
                print(f"UL datarate of MAC: {bpsToMbps(ul_data_rate)} Mbps\nDL datarate of MAC: {bpsToMbps(dl_data_rate)} Mbps\n===============================================")

                #reset states
                self.prev_ul_total_bytes = ind.ue_stats[i].ul_aggr_tbs
                self.prev_dl_total_bytes = ind.ue_stats[i].dl_aggr_tbs
            self.prev_tstamp = ind.tstamp

if (__name__=="__main__"):
    #E42 Setup
    xapp_sdk.init()
    
    #get available E2 Nodes
    conn = xapp_sdk.conn_e2_nodes()
    assert(len(conn)>0)
    
    
    handlers = []
    for i in range(0, len(conn)):
        print(f"Global E2 Node [{i}]: PLMN MCC = {conn[i].id.plmn.mcc}, MNC = {conn[i].id.plmn.mnc}")
        MAC_cb = MACCallback()
        
        #Report Subscription
        hndlr = xapp_sdk.report_mac_sm(conn[i].id, xapp_sdk.Interval_ms_1, MAC_cb)
        handlers.append(hndlr)
        
    #keep the subscription for 10 sec
    time.sleep(10)
    
    for i in range(len(handlers)):
        #Cancel Report Subscription
        xapp_sdk.rm_report_mac_sm(handlers[i])
        
    while (xapp_sdk.try_stop==0):
        time.sleep(1)