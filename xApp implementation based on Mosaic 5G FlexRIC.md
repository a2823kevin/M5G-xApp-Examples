xApp implementation based on Mosaic 5G FlexRIC
===

目錄
---
- [FlexRIC簡介](#FlexRIC簡介)
- [FlexRIC下載&安裝](#FlexRIC下載amp安裝)
  * [安裝依賴](#安裝依賴)
  * [下載](#下載FlexRIC)
  * [編譯](#編譯FlexRIC)
  * [額外步驟](#額外步驟)
- [E2 Node、RIC、xApp的運作解析](#E2-Node、RIC、xApp的運作解析)
  * [E2 Setup](#E2-Setup)
  * [E42 Setup](#E42-Setup)
  * [Report Subscription](#Report-Subscription)
- [xApp範例](#xApp範例程式)
  * [MAC層上下行流量監測](#MAC層上下行流量監測程式碼)
- [參考資料](#參考資料)

FlexRIC簡介
---
FlexRIC為Mosaic 5G所研發的一款SDK，其中包含Near-RT RIC(RAN intelligent controller)和幾種xApp的實作。

RIC與E2 Node之間的溝通介面稱為E2，而傳輸於此介面的控制訊息則使用E2AP(E2 Application Protocol)。

![E2](https://cdn.discordapp.com/attachments/399195201714913280/1106959294412365956/E2.png =50%x)RIC與E2 Node間的溝通介面: E2

FlexRIC的設計中包含了許多**SM(Service Model)**，用以**描述對各種RAN Function提供的服務(e.g. Report, Control)**、各服務的E2AP Procedures(e.g. indication Request, Control Request)，亦或服務所使用到的**Information Elements**。

![IE&E2AP](https://cdn.discordapp.com/attachments/399195201714913280/1106962525309894778/IEnE2AP.png =70%x)SM中的IE與E2AP的對應關係

一旦SM被定義，則**xApp、RIC及E2 Node皆須根據其產生相應的函式庫**，以便三者在互相溝通時能正確的編碼/解碼訊息，並執行對應的功能。

由於O-RAN未對xApp及RIC間的溝通介面作出定義，其他方案的xApp實作將難以與RIC分離運行於不同機器。而Mosaic 5G在FlexRIC中**提出了E42介面，實現了xApp與RIC的分離方法**，使xApp能夠以「隨插即用」的方式與RIC相互構通，也使xApp的開發與運行更加彈性。

![E42 interface](https://cdn.discordapp.com/attachments/399195201714913280/1106966571156512929/E42.png =70%x) xApp與RIC間的溝通介面: E42

FlexRIC下載&安裝
---
### 安裝依賴
***CMake***
```
sudo apt install cmake
```
***Swig***

install swig dependency
```
sudo apt install libpcre2-dev
```
install swig
```
git clone https://github.com/swig/swig.git
cd swig
./autogen.sh
./configure --prefix=/usr/
make -j $(nproc)
sudo make install
```
***FlexRIC***
```
sudo apt install libsctp-dev python3.8 cmake-curses-gui python3-dev
```
### 下載FlexRIC
```
git clone https://gitlab.eurecom.fr/mosaic5g/flexric.git
```
### 編譯FlexRIC
```
cd flexric
mkdir build
cd build
cmake ..
make -j $(nproc)
```
### 額外步驟
---
#### *於裝置安裝FlexRIC*
**E2 Node、RIC及xApp的運行仰賴各SM的函式庫**，在三者所運行的裝置上須先安裝編譯出的檔案。
```
cd <PATH_TO_FLEXRIC>/build
sudo make install
```
SM函式庫會被安裝於/usr/local/lib/flexric，以下為其目錄架構
```
/usr/local/lib/flexric
├── libgtp_sm.so
├── libkpm_sm.so
├── libmac_sm.so
├── libpdcp_sm.so
├── librlc_sm.so
├── libslice_sm.so
├── libT1_sm.so
└── libtc_sm.so
```
---
#### *安裝FlexRiC對OAI RAN的補丁*
FlexRIC針對OpenAirInterface、srsRAN提供了**實現E2 Agent功能**的補丁，使其能作為實際的E2 Node運行。
```
cd <PATH_TO_OAI>
git checkout 2022.41
git am <PATH_TO_FLEXRIC>/multiRAT/oai/oai.patch --whitespace=nowarn
source oaienv
cd cmake_targets/ran_build/build
make nr-softmodem -j $(nproc)
```
若有**修改或新增SM**，則需**再對<PATH_TO_OAI>/executables內的程式再作調整**，並重新執行上方nr-softmodem的編譯步驟。

E2 Node、RIC、xApp的運作解析
---
### E2 Setup
在E2 Node(e.g. OAI gNB)及RIC的初始化階段，會先從/usr/local/lib/flexric讀入可用的SM函式庫。

***OAI gNB***
```
[E2 AGENT]: Initializing ... 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libslice_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libpdcp_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libtc_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libgtp_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libT1_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libmac_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/librlc_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libkpm_sm.so
```
***Near-RT RIC***
```
Setting path -p for the shared libraries to /usr/local/lib/flexric/
[NEAR-RIC]: Initializing 
[NEAR-RIC]: Loading SM ID = 145 with def = SLICE_STATS_V0 
[NEAR-RIC]: Loading SM ID = 144 with def = PDCP_STATS_V0 
[NEAR-RIC]: Loading SM ID = 146 with def = TC_STATS_V0 
[NEAR-RIC]: Loading SM ID = 148 with def = GTP_STATS_V0 
[NEAR-RIC]: Loading SM ID = 200 with def = T1_STATS_V0 
[NEAR-RIC]: Loading SM ID = 142 with def = MAC_STATS_V0 
[NEAR-RIC]: Loading SM ID = 143 with def = RLC_STATS_V0 
[NEAR-RIC]: Loading SM ID = 147 with def = ORAN-E2SM-KPM
```
接下來E2 Node會將可用的SM資訊透過E2 Setup request告知RIC。
```
[E2-AGENT]: Sending setup request
```
RIC接收到請求後會確認自身是否支援此E2 Node請求的服務，並記錄下E2 Node的資訊以供之後xApp的調用。完成以上步驟後RIC將回傳E2 Setup response給E2 Node。
```
[E2AP] Received SETUP-REQUEST from PLMN 505. 1 Node ID 3584 RAN type ngran_gNB
[NEAR-RIC]: Accepting RAN function ID 142 with def = MAC_STATS_V0 
[NEAR-RIC]: Accepting RAN function ID 143 with def = RLC_STATS_V0 
[NEAR-RIC]: Accepting RAN function ID 144 with def = PDCP_STATS_V0 
[NEAR-RIC]: Accepting RAN function ID 145 with def = SLICE_STATS_V0 
[NEAR-RIC]: Accepting RAN function ID 146 with def = TC_STATS_V0 
[NEAR-RIC]: Accepting RAN function ID 147 with def =  
[NEAR-RIC]: Accepting RAN function ID 148 with def = GTP_STATS_V0 
[NEAR-RIC]: Accepting RAN function ID 200 with def = T1_STATS_V0
```
待E2 Node接收回覆，E2 Setup完成。
```
[E2-AGENT]: SETUP-RESPONSE received
[E2-AGENT]: stopping pending
```
![E2 Setup](https://cdn.discordapp.com/attachments/399195201714913280/1107232111318007888/E2_Setup.png =80%x) E2 Setup的流程

### E42 Setup
xApp在初始化階段同樣會以SDK先從/usr/local/lib/flexric讀入可用的SM函式庫，並將可用的SM資訊透過E42 Setup request告知RIC。
```
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libslice_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libpdcp_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libtc_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libgtp_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libT1_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libmac_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/librlc_sm.so 
[E2 AGENT]: Opening plugin from path = /usr/local/lib/flexric/libkpm_sm.so 
Loading SM ID = 145 with def = SLICE_STATS_V0 
Loading SM ID = 144 with def = PDCP_STATS_V0 
Loading SM ID = 146 with def = TC_STATS_V0 
Loading SM ID = 148 with def = GTP_STATS_V0 
Loading SM ID = 200 with def = T1_STATS_V0 
Loading SM ID = 142 with def = MAC_STATS_V0 
Loading SM ID = 143 with def = RLC_STATS_V0 
Loading SM ID = 147 with def = ORAN-E2SM-KPM
[xApp]: E42 SETUP-REQUEST sent
```
RIC接收到請求後同樣會確認自身是否支援xApp請求的服務，**iApp會分派ID給xApp，並將可控制的E2 Node資訊透過E42 Setup response回傳給xApp**。
```
[iApp]: E42 SETUP-REQUEST received
[iApp]: E42 SETUP-RESPONSE sent
```
待xApp接收回覆，E42 Setup完成。
```
[xApp]: E42 SETUP-RESPONSE received
[xApp]: xApp ID = 7 
Registered E2 Nodes = 1
```
![E42 Setup](https://cdn.discordapp.com/attachments/399195201714913280/1107250086574043167/E42_Setup.png =80%x) E42 Setup的流程

### Report Subscription
xApp在完成E2 Setup後可根據自身需求對各RAN function進行report subscription，以定期收取indication。進行訂閱時需**指定E2 Node的ID，以及報告間隔**，這些設定會附帶於**E42 Subscription request**傳送至RIC。
```
Generated of req_id = 1 
[xApp]: RIC SUBSCRIPTION REQUEST sent
```
RIC接收到請求後會根據請求的資訊對指定的E2 Node發送**E2 Subscription request**，確認來自xApp的訂閱是否有效。
```
[iApp]: SUBSCRIPTION-REQUEST xapp_ric_id->ric_id.ran_func_id 142  
[E2AP] SUBSCRIPTION REQUEST generated
```
若E2 Node的回覆為訂閱成功，RIC會將此結果作為E2 Subscription response回傳至xApp。
```
[xApp]: SUBSCRIPTION RESPONSE received
Pending event size before remove = 1 
[xApp]: Successfully SUBSCRIBED to ran function = 142
```

![Subscription Setup](https://cdn.discordapp.com/attachments/399195201714913280/1107305429438038037/Subscription_Setup.png =70%x) Subscription Setup的流程

經過Subscription Setup的流程，xApp便能定期接收來自E2 Node傳送給RIC的indication，直到訂閱被取消。開發者也能**自訂Callback function來指定接收到indication時要進行的動作**。以下是一個將indication從被製造到xApp接收的時間差印出的Callback範例(以Python實作): 
```python=
class MACCallback(ric.mac_cb):
    def __init__(self):
        ric.mac_cb.__init__(self)

    def handle(self, ind):
        if (len(ind.ue_stats)>0):
            t_now = time.time_ns() / 1000.0
            t_mac = ind.tstamp / 1.0
            t_diff = t_now - t_mac
            print(f"time difference between E2 Node & xApp: {t_diff} ms")
```
若在Subscription Setup時指定使用此Callback，xApp在接收到indication時便能看到類似以下的輸出結果: 
```
time difference between E2 Node & xApp: 144.25 ms
time difference between E2 Node & xApp: 135.75 ms
time difference between E2 Node & xApp: 276.5 ms
time difference between E2 Node & xApp: 134.0 ms
time difference between E2 Node & xApp: 218.75 ms
time difference between E2 Node & xApp: 124.25 ms
time difference between E2 Node & xApp: 174.25 ms
time difference between E2 Node & xApp: 123.25 ms
time difference between E2 Node & xApp: 118.25 ms
time difference between E2 Node & xApp: 138.0 ms
...
```
![Indication Reception](https://cdn.discordapp.com/attachments/399195201714913280/1107310278602924142/Indication_Reception.png =70%x) xApp接收Indication的流程

xApp範例程式
---
FlexRIC使用了SWIG來支援使用腳本語言(e.g. Python)編寫xApp，以下為2個使用Python搭配xApp SDK編寫的xApp範例。
### MAC層上下行流量監測([程式碼](https://github.com/a2823kevin/M5G-xApp-Examples/blob/main/mac_datarate_monitoring.py))
在此程式中，我們的目標是利用MAC SM在Indication提供的資訊來監測上下行的流量。

因為要用利用到Indication，我們可以先**定義Report Callback被呼叫**時計算流量的方法。
```python=
class MACCallback(xapp_sdk.mac_cb):
    def __init__(self):
        xapp_sdk.mac_cb.__init__(self)
        self.prev_tstamp = 0
        self.prev_ul_total_bytes = 0
        self.prev_dl_total_bytes = 0

    def handle(self, ind):
        if (len(ind.ue_stats)>0):
            for i in range(len(ind.ue_stats)):

                interval = (ind.tstamp-self.prev_tstamp) / 1e6
                ul_data_rate = (ind.ue_stats[i].ul_aggr_tbs-self.prev_ul_total_bytes) * 8 / interval
                dl_data_rate = (ind.ue_stats[i].dl_aggr_tbs-self.prev_dl_total_bytes) * 8 / interval
                if (ul_data_rate<=0 or dl_data_rate<=0):
                    return
                
                print(f"UL datarate of MAC: {bpsToMbps(ul_data_rate)} Mbps\nDL datarate of MAC: {bpsToMbps(dl_data_rate)} Mbps\n===============================================")

                self.prev_ul_total_bytes = ind.ue_stats[i].ul_aggr_tbs
                self.prev_dl_total_bytes = ind.ue_stats[i].dl_aggr_tbs
            self.prev_tstamp = ind.tstamp
```
MAC Indication中含有timestamp(indication被E2 Node填充的時間)，以及上下行被傳輸的數據量等資訊。我們可以在indication到達時**將目前累積減去上次累積的數據量，再除以兩次的時間差**，便可得到流量大小。
$$datarate(bps) = \frac{8\times\Delta byte}{\Delta time}$$
計算完流量後須將上次紀錄的資訊更新為目前資訊，讓下次接收Indication時也能正確計算流量。

在程式的開始須先執行E42 Setup的步驟，建立與RIC的連接並確保SM能夠正常使用。
```python=
xapp_sdk.init()
```
E42 Setup結束後，我們便可得知目前連接至RIC的E2 Nodes。若沒有任何E2 Node連接，便結束此xApp。
```python=
conn = xapp_sdk.conn_e2_nodes()
assert(len(conn)>0)
```
得到E2 Node的資訊後，我們便可指定要發送Report Subscription給哪個E2 Node以監測其MAC流量，在訂閱時也可指定報告間隔。Subscription Setup的Response會形成Handler，可供之後取消Report Subscription使用。在此程式我們對所有E2 Node以1ms為報告間隔進行訂閱，並紀錄Handlers。
```python=
handlers = []
for i in range(0, len(conn)):
    print(f"Global E2 Node [{i}]: PLMN MCC = {conn[i].id.plmn.mcc}, MNC = {conn[i].id.plmn.mnc}")
    MAC_cb = MACCallback()
    hndlr = xapp_sdk.report_mac_sm(conn[i].id, xapp_sdk.Interval_ms_1, MAC_cb)
    handlers.append(hndlr)
```
因為Report Callback的運行與主程式屬於不同線程，在Report的訂閱期間我們必**須自訂一個主程式的等待時間防止程式立刻結束**。在此程式我們使Report能持續10秒，約能接收10000個indication。
```python=
time.sleep(10)
```
在等待時間結束後，我們便能用之前紀錄的Handlers來取消對各E2 Node的訂閱，最後結束xApp程式。
```python=
for i in range(len(handlers)):
    xapp_sdk.rm_report_mac_sm(handlers[i])
        
while (xapp_sdk.try_stop==0):
    time.sleep(1)
```
此範例中，我使用了OAI的[RF simulator](https://gitlab.eurecom.fr/oai/openairinterface5g/-/blob/develop/radio/rfsimulator/README.md)來運行E2 Node及UE，可產生約1.2Mbps的流量。以下為各程式的啟動順序。
$$RIC\rightarrow gNB\rightarrow nrUE\rightarrow xApp$$
xApp在執行期間將印出監測到的MAC流量，以下為部分輸出結果: 
```
UL datarate of MAC: 1.2504067075459893 Mbps
DL datarate of MAC: 1.1863346264547616 Mbps
===============================================
UL datarate of MAC: 1.249 Mbps
DL datarate of MAC: 1.185 Mbps
===============================================
UL datarate of MAC: 1.249 Mbps
DL datarate of MAC: 1.185 Mbps
===============================================
UL datarate of MAC: 1.2485318005747843 Mbps
DL datarate of MAC: 1.1845557915781584 Mbps
===============================================
UL datarate of MAC: 1.2491561445180648 Mbps
DL datarate of MAC: 1.1851481435179398 Mbps
===============================================
UL datarate of MAC: 1.109113109113109 Mbps
DL datarate of MAC: 1.0522810522810524 Mbps
===============================================
UL datarate of MAC: 1.2507197396420078 Mbps
DL datarate of MAC: 1.1866316184754035 Mbps
===============================================
UL datarate of MAC: 1.2485318005747843 Mbps
DL datarate of MAC: 1.1845557915781584 Mbps
===============================================
UL datarate of MAC: 1.427836524721349 Mbps
DL datarate of MAC: 1.3546727636467564 Mbps
===============================================
UL datarate of MAC: 1.1098522714650672 Mbps
DL datarate of MAC: 1.0529823392202597 Mbps
===============================================
```
RIC、E2 Node、UE、xApp聯合運行的[asciinema紀錄檔](https://github.com/a2823kevin/M5G-xApp-Examples/blob/main/mac_datarate_monitoring.cast)

參考資料
---
https://gitlab.eurecom.fr/mosaic5g/flexric  
https://gitlab.eurecom.fr/oai/openairinterface5g  
https://hackmd.io/@Min-xiang/H1bOyKUU5  