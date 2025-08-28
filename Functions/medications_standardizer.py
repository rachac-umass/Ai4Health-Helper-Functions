import numpy as np
import time
import requests
import re

class MedicationsStandardizer:
    def convert_rxcui_to_ATC(self, rxcui: int, ATC_level: int) -> list:
        '''
        Converts an RxCUI code to a list of ATC codes of the specified level.

        Args:
            rxcui (int): RxCUI code for a medication.
            ATC_level (int): Level of the ATC code (1-4).

        Returns:
            list: Unique ATC codes at the requested level or error message if not found.
        '''
        response_rx = requests.get(f'https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?rxcui={rxcui}&relaSource=ATC')
        atc_codes = []
        if response_rx.status_code != 200:
            return "Not found(status code at rxcui-> atc)"
        try:
            for data in response_rx.json()['rxclassDrugInfoList']['rxclassDrugInfo']:
                atc_codes.append(data['rxclassMinConceptItem']['classId'])
        except:
            try:
                if response_rx.json() == {}:
                    response_rx = requests.get(f'https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?caller=RxNav&rxcui={rxcui}&relaSource=ATCPROD')
                    atc_codes = [item["rxclassMinConceptItem"]["classId"]
                        for item in response_rx.json()["rxclassDrugInfoList"]["rxclassDrugInfo"]
                        if item["minConcept"]["rxcui"] == rxcui]
            except:
                return 'Not found(at rxcui-> all atc codes)'
        atc_codes = np.unique([atc_code[:ATC_level+1] for atc_code in atc_codes]).tolist()
        return atc_codes

    def convert_rxcui_to_active_ingrident(self, rxcui: int) -> list:
        '''
        Converts an RxCUI code to a list of active ingredient names.

        Args:
            rxcui (int): RxCUI code for a medication.

        Returns:
            list: List of sorted active ingredient names.
        '''
        url = f'https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/allrelated.json'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        ingredients = []
        for group in data.get('allRelatedGroup', {}).get('conceptGroup', []):
            if group.get('tty') == 'IN':
                for concept in group.get('conceptProperties', []):
                    ingredients.append(concept['name'])
        return ingredients

    def convert_ndc_to_ATC(self, ndc: int, ATC_level = None):
        '''
        Converts an NDC code to a list of ATC codes at the given level.

        Args:
            ndc (int): The NDC code.
            ATC_level (int): ATC code level (1 - 4).

        Returns:
            list: List of ATC codes.
        '''
        assert type(ATC_level) is int, "ATC level should be int and takes value from 1 to 4."
        assert 1 <= ATC_level <= 4, "ATC level valid values: 1, 2, 3 and 4"
        return self.convert_ndc_to_atc(ndc)

    def ndc_standaradizer_10_to_11_digit(self, ndc: str) -> str:
        '''
        Converts a 10-digit NDC code (with dashes) to an 11-digit NDC code (with dashes).

        Args:
            ndc (str): NDC code in 10-digit format with '-' delimiter.

        Returns:
            str: NDC code in 11-digit format with '-' delimiter.
        '''
        if len(ndc) == 11:
            return ndc
        assert len(ndc) == 13, 'The ndc code length is not 13 (10 digits + 3 hypens)'
        digits = re.sub(r'\D', '', ndc)
        if len(digits) != 10:
            raise ValueError("Input must contain exactly 10 digits.")
        parts = re.split(r'-', ndc)
        if len(parts) == 3:
            if len(parts[0]) == 4 and len(parts[1]) == 4 and len(parts[2]) == 2:
                return '0' + digits[0:4] + '-' + digits[4:8] + '-' + digits[8:10]
            elif len(parts[0]) == 5 and len(parts[1]) == 3 and len(parts[2]) == 2:
                return digits[0:5] + '-' + '0' + digits[5:8] + '-' + digits[8:10]
            elif len(parts[0]) == 5 and len(parts[1]) == 4 and len(parts[2]) == 1:
                return digits[0:5] + '-' + digits[5:9] + '-' + '0' + digits[9]
        raise ValueError("")

    def convert_ndc_to_atc(self, ndc: int, ATC_level = None, time_sleep = None) -> list:
        '''
        Converts an 11-digit NDC code to a list of ATC codes at a specified level.

        Args:
            ndc (int or str): NDC code as integer or string.
            ATC_level (int): ATC code level (1-4).
            time_sleep (float or None): Optional time to wait between requests.

        Returns:
            list: List of ATC codes at required level or error message.
        '''
        ndc = str(ndc)
        assert 1 <= ATC_level <= 4, "level keyword should be between 1 and 4"
        assert len(ndc) == 11, "Number of digits in ndc code should be equal to 11"
        response = requests.get("https://rxnav.nlm.nih.gov/REST/ndcstatus.json?ndc=" + ndc)
        if response.status_code != 200:
            print(f'Error in ndc code: {ndc} at retriving rxcui')
            return "Not found(status code at ndc -> rxcui)"
        response_ndc = response.json()
        try:
            rxcui = [data['activeRxcui']  for data in response_ndc['ndcStatus']['ndcHistory'] if data['activeRxcui']][-1]
        except:
            print('failed at getting rxcui',ndc)
            return "Not found(activeRxcui key not found)"
        return self.convert_rxcui_to_ATC(rxcui, ATC_level = ATC_level)
