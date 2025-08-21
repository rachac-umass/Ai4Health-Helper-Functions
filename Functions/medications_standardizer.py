import numpy as np
import pandas as pd
import time
import requests

### TO-DO ###
# To standardize medications to acive ingrident/ ATC codes (different levels)  ***create class***
#
class standardize_medication():
    def __init__(self,ndc = None, rxcui = None):
        self.ndc = ndc
        self.rxcui = rxcui

        assert bool(self.ndc) ^ bool(self.rxcui), "Both ndc and rxcui cannot be none,"
        

    def convert_rxcui_to_atc




def convert_ndc_to_atc_or_active_ingrident(ndc: str, level = 4):
    '''
    '''

    time.sleep(0.15)
    assert 1 <= level <= 4, "level keyword should be between 1 and 4"
    assert len(ndc) == 11, "Number of digits in ndc code should be equal to 11"
    
    ### get rxcui
    response = requests.get("https://rxnav.nlm.nih.gov/REST/ndcstatus.json?ndc=" + ndc)
    # print(response.json())

    if response.status_code != 200:

        print(f'Error in ndc code: {ndc} at retriving rxcui')
        return None

    response_ndc = response.json()
    try:
        rxcui = [data['activeRxcui']  for data in response_ndc['ndcStatus']['ndcHistory'] if data['activeRxcui']][-1]
    except:
        print('failed at getting rxcui',ndc)
        return None
    response_rx = requests.get(f'https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?rxcui={rxcui}&relaSource=ATC')

    atc_codes = []
    
    if response_rx.status_code != 200:

        print(f'Error in ndc code: {ndc} at retriving atc codes')
        return None

    try:
        for data in  response_rx.json()['rxclassDrugInfoList']['rxclassDrugInfo']:
            atc_codes.append(data['rxclassMinConceptItem']['classId'])
    except:
            try:
                if response_rx.json() == {}:
                    
                    response_rx = requests.get(f'https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?caller=RxNav&rxcui={rxcui}&relaSource=ATCPROD')
                    # Collecting all ATC class IDs for rxcui '876193'
                    atc_codes = [item["rxclassMinConceptItem"]["classId"]
                         for item in response_rx.json()["rxclassDrugInfoList"]["rxclassDrugInfo"]
                         if item["minConcept"]["rxcui"] == rxcui]
                
            except:
                print('Failed at getting atc codes:',ndc)
                return None
        
    atc_codes = np.unique([atc_code[:level+1] for atc_code in atc_codes]).tolist()
    
    return atc_codes