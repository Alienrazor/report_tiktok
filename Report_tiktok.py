import hashlib
import json
import requests
import uuid
from time import time
from copy import deepcopy
import random
import os
class CryptoHeaders:
    def __init__(self, param="", stub="", cookie=""):
        self.param = param
        self.stub = stub
        self.cookie = cookie
        self.current_time = int(time())
        self.gorgon_values = self._compute_gorgon_values()
        self.debug_values = []
        self.state = [t]
        self.intermediate_values = []
        self.final_values = []

    def _hash_to_bytes(self, data):
        if data:
            return hashlib.md5(data.encode('utf-8')).digest()
        return b'\x00' * 16

    def generate_session_ids(self):
        new_uuid = str(uuid.uuid4()).replace('-', '')
        sid_tt = f"sid_tt={new_uuid[:16]}; "
        sessionid = f"sessionid={new_uuid}; "
        sessionid_ss = f"sessionid_ss={new_uuid}; "
        return sid_tt, sessionid, sessionid_ss

    def _compute_gorgon_values(self):
        gorgon = []
        gorgon.extend(self._hash_to_bytes(self.param))
        gorgon.extend(self._hash_to_bytes(self.stub))
        gorgon.extend(self._hash_to_bytes(self.cookie))
        gorgon.extend([0x00, 0x08, 0x10, 0x09])
        gorgon.extend(self._int_to_bytes(self.current_time))
    #    print("Gorgon:", [self._format_hex(b) for b in gorgon])
        return gorgon

    def _int_to_bytes(self, value):
        return [(value >> (8 * i)) & 0xFF for i in range(4)]

    def _format_hex(self, num):
        return f"{num:02x}"

    def _swap_nibbles(self, num):
        hex_str = f"{num:02x}"
        return int(hex_str[1] + hex_str[0], 16)

    def _reverse_bits(self, num):
        return int(f"{num:08b}"[::-1], 2)

    def _generate_state(self):
        state = list(range(256))
        tmp = ''
        for i in range(256):
            prev = tmp if tmp else state[i - 1]
            modifier = self.gorgon_values[i % 8]
            if prev == 0x05 and i != 1 and tmp != 0x05:
                prev = 0
            new_value = (prev + i + modifier) % 256
            tmp = new_value if new_value < i else ''
            state[i] = state[new_value]
        self.state = state
    #    print("Generated e:", [self._format_hex(b) for b in state])
        return state

    def _initialize_debug(self, state):
        debug = [0] * 20
        temp_state = deepcopy(state)
        for i in range(20):
            prev_value = debug[i - 1] if i > 0 else 0
            new_index = (state[i + 1] + prev_value) % 256
            debug[i] = temp_state[new_index]
            double_value = (debug[i] * 2) % 256
            temp_state[i + 1] = temp_state[double_value]
            debug[i] ^= temp_state[double_value]
        self.debug_values = debug
    #    print("Initialized :", [self._format_hex(b) for b in debug])
        return debug

    def _calculate_values(self, debug):
        for i in range(20):
            byte = debug[i]
            swapped = self._swap_nibbles(byte)
            next_byte = debug[(i + 1) % 20]
            xored = swapped ^ next_byte
            reversed_bits = self._reverse_bits(xored)
            modified = reversed_bits ^ 20
            debug[i] = (~modified) & 0xFF
            self.intermediate_values.append({
                'step': i,
                'byte': self._format_hex(byte),
                'swapped': self._format_hex(swapped),
                'xored': self._format_hex(xored),
                'reversed_bits': self._format_hex(reversed_bits),
                'modified': self._format_hex(modified),
                'final': self._format_hex(debug[i])
            })
    #    print("Intermediate ", self.intermediate_values)
        return debug

    def generate_headers(self):
        sid_tt, sessionid, sessionid_ss = self.generate_session_ids()
        state = self._generate_state()
        debug = self._initialize_debug(state)
        calculated_values = self._calculate_values(debug)
        result = ''.join(self._format_hex(byte) for byte in calculated_values)
        xgorgon = f"8402{self._format_hex(self.gorgon_values[7])}{self._format_hex(self.gorgon_values[3])}" \
                  f"{self._format_hex(self.gorgon_values[1])}{self._format_hex(self.gorgon_values[6])}{result}"
 #       print("X-Gorgon :", xgorgon)
#        print("X-Khronos:", str(self.current_time))
        self.final_values = {
            'X-Gorgon': xgorgon,
            'X-Khronos': str(self.current_time),
            'sessionid': sessionid,
            'sid_tt': sid_tt,
            'sessionid_ss': sessionid_ss
        }
        return self.final_values

 
    def compute_stub(data):
        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode('utf-8')
        if not data:
            return "00000000000000000000000000000000"
        stub = hashlib.md5(data).hexdigest().upper()
 #       print("Computed ", stub)
        return stub

def get_cookies_and_tokens():
    cookies_and_tokens = {}
    try:
        cookies = requests.get('https://www.tiktok.com/login').cookies.get_dict()
        cookies_and_tokens['msToken'] = cookies.get('msToken', 'Not found')
        cookies_and_tokens['odin_tt'] = cookies.get('odin_tt', 'Not found')
        cookies_and_tokens['store-idc'] = cookies.get('store-idc', 'Not found')
        cookies_and_tokens['tt-target-idc'] = cookies.get('tt-target-idc', 'Not found')
        cookies_and_tokens['tt_csrf_token'] = cookies.get('tt_csrf_token', 'Not found')
        cookies_and_tokens['ttwid'] = cookies.get('ttwid', 'Not found')
    except Exception as e:
        print(f"Failed : {e}")
    return cookies_and_tokens
def headers_xc():
    try:
        response = requests.post('https://api22-normal-c-alisg.tiktokv.com/passport/data/SAJAD/?passport-sdk-version=19&iid=7372841843832473349&device_id=7194351170030650885&ac=WIFI&channel=googleplay&aid=1233&app_name=musical_ly&version_code=310503&version_name=31.5.3&device_platform=android&os=android&ab_version=31.5.3&ssmix=a&device_type=Infinix+X6816&device_brand=Infinix&language=ar&os_api=30&os_version=11').cookies.get_dict()
        msToken = response['msToken']
        odin_tt = response['odin_tt']
        store_idc = response['store-idc']
        tt_target_idc = response['tt-target-idc']
        print(msToken, odin_tt, store_idc, tt_target_idc)

        coo = requests.get('https://www.tiktok.com/login').cookies.get_dict()
        tt_csrf_token = coo.get('tt_csrf_token', 'Not found')
        ttwid = coo.get('ttwid', 'Not found')
        print(ttwid)
    
    except Exception as e:
        print(f"Failed to get headers: {e}")

banner =(""" \033[0;91m                
                      ::             .^:                    
                    5#~               .Y&J                  
                .: &@^                  5@# !               
                &P:@@                   ~@@~@J              
                &@&@@G       ....~     .&@@@@Y              
              .?~&@@@G     !P@@@@7      @@@@G~J             
               ?&#@@@P^.     !@@&     ^^&@@&&&^             
                .5#&@@GBPJ!:.Y@@@?^?YGG#@@&B?               
                 !B&&@@@@@@@@@@@@@@@@@@@@&#G:               
                  :P&@@&@@@@@@@@@@@@@&&@@B7                 
                     .~!:^G@&@@@@@@J:~!:                    
                       ^?P5:.@@@G !P5!.                     
                        :.  G@@@@!  :.                      
                           J@&@&@@^                         
                          :&&B&#&##                         
                          :Y#G&#&Y5                         
                            Y5@#B:                          
                            ^J@#Y                           
                             ~@#^                           
                             .@#                            
                              &B                            
                              &G                            
                              #5                            
                              G?                            
                                                           
\033[96;1m______________________________________________________ \033[93;1m \n
\033[1;32m          AUTHOR : Alienrazor
\033[1;32m          GITHUB : Alienrazor
 \033[1;32m         TOOL NAME : Report TikTok
\033[96;1m______________________________________________________ \33
                              

""")

if __name__ == "__main__":
    os.system('clear')
    print(banner) 
    id = input("|•> id :  ")
    params = f'report_type=video&object_id={id}&owner_id={id}&hide_nav_bar=1&lang=ar&report_desc&uri&reason=9007&category&request_tag_from=h5&manifest_version_code=350302&_rticket=1723485623998&app_language=ar&app_type=normal&iid='+str(random.randint(30000, 79999))+'&channel=googleplay&device_type=Infinix+X6816&language=ar&host_abi=arm64-v8a&locale=ar&resolution=720*1568&openudid=2ddbb6c1ff7e8267&update_version_code=350302&ac2=lte&cdid=9d696dc8-d137-41b0-beb3-da3ed6656a64&sys_region=IQ&os_api=30&timezone_name=Asia%2FBaghdad&dpi=295&carrier_region=IQ&ac=4g&device_id=7401074425095489029&os_version=12&timezone_offset=10800&version_code=350302&app_name=musically_go&ab_version=35.3.2&version_name=35.3.2&device_brand=Infinix&op_region=IQ&ssmix=a&device_platform=android&build_number=35.3'

    cookie = ''
    crypto_headers = CryptoHeaders(param=params, cookie=cookie)
    headers = crypto_headers.generate_headers()
    x_gorgon = headers['X-Gorgon']
    x_khronos = headers['X-Khronos']
    sessionid = headers['sessionid']
    sid_tt = headers['sid_tt']
    sessionid_ss = headers['sessionid_ss']
    cookies_and_tokens = get_cookies_and_tokens()
    msToken = cookies_and_tokens.get('msToken', '')
    odin_tt = cookies_and_tokens.get('odin_tt', '')
    store_idc = cookies_and_tokens.get('store-idc', '')
    tt_target_idc = cookies_and_tokens.get('tt-target-idc', '')
    ttwid = cookies_and_tokens.get('ttwid', '')

    request_headers = {
        'X-Gorgon': x_gorgon,
        'X-Khronos': x_khronos,
        'sessionid': sessionid,
        'sid_tt': sid_tt,
        'sessionid_ss': sessionid_ss,
        'User-Agent': 'TikTok 35.3.2 rv:350302 (Infinix; Android 12; ar; Build/QP1A.190711.020; Cronet/TTNetVersion:06ba982e 2022-03-18 QuicVersion:d0d2b424 2022-01-28)',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': f"store-idc={store_idc}; tt-target-idc={tt_target_idc}; ttwid={ttwid}; odin_tt={odin_tt}; msToken={msToken}",
    }
    while True:
        try:
        	response = requests.post('https://api16-normal-c-alisg.tiktokv.com/aweme/v2/aweme/feedback/', data=params, headers=request_headers)
        	print(response.text)
        except:
        	pass    
