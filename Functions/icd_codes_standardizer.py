import pandas as pd
import polars as pl
import pyreadr
from icdmappings import Mapper

class ICDStandardizer:
    def __init__(self):
        # Load the data files containing mappings between ICD codes and Phecodes.
        self.icd10_phe = pl.read_csv('./icd_code_to_phecode/Phecode_map_v1_2_icd10cm_beta.csv')
        self.icd9_phe_v1 = pl.read_csv('./icd_code_to_phecode/phecode_map_v1_2_icd9.csv', infer_schema_length=100000)
        self.icd9_phe_v2 = pyreadr.read_r("./icd_code_to_phecode/phemap (1).rda")['phemap'].drop_duplicates(subset=['icd9'])
        
        # Create dictionaries for mapping ICD codes to Phecodes.
        self.icd10_phe_dict = dict(zip(self.icd10_phe['ICD10CM'].to_list(), self.icd10_phe['PHECODE'].to_list()))
        self.icd9_phe_dict_v1 = dict(zip(self.icd9_phe_v1['ICD9'].to_list(), self.icd9_phe_v1['PheCode'].to_list()))
        self.icd9_phe_dict_v2 = dict(zip(self.icd9_phe_v2['icd9'].to_list(), self.icd9_phe_v2['phecode'].to_list()))

    def convert_icd9_to_icd10(self, icd9):
        '''
        Converts an ICD-9 code to an ICD-10 code.

        Args:
            icd9: str - The ICD-9 code to be converted.

        Returns:
            str: The corresponding ICD-10 code with a prefix 'ICD10CM:', or 'ICD9CM:' followed by the original code if conversion fails.
        '''
        mapper = Mapper()
        icd10_code = mapper.map(icd9, source='icd9', target='icd10')
        if icd10_code:
            return 'ICD10CM:' + icd10_code[:3] + '.' + icd10_code[3:]
        else:
            return 'ICD9CM:' + icd9

    def get_first_n_char_icdcode(self, icd_code, n=None):
        '''
        Retrieves the first n characters of an ICD code.

        Args:
            icd_code: str - The ICD code to truncate. The code shouldn't have any prefix
            n: int, optional - The number of characters to retrieve. If not specified, returns the entire code.

        Returns:
            str: The truncated ICD code.
        '''
        return icd_code[:n]

    def standardize_elements_icd10(self, dx_type: int, dx: str) -> str:
        '''
        Standardizes an ICD code to ICD-10 format.

        Args:
            dx_type: int - The type of ICD code (9 for ICD-9, 10 for ICD-10).
            dx: str - The diagnosis code. The code shouldn't have any prefix

        Returns:
            str: The standardized ICD-10 code with prefix 'ICD10CM:', or original with 'ICD9CM:' if conversion fails.
        '''
        mapper = Mapper()
        if dx_type == 10:
            return dx
        elif dx_type == 9:
            icd10_code = mapper.map(dx.replace('.', ''), source='icd9', target='icd10')
            if icd10_code is None:
                return "ICD9CM:" + dx
            else:
                return "ICD10CM:" + icd10_code[:3] + '.' + icd10_code[3:]

    def icd_codes_to_phewas_codes(self, icd_code: str, icd_type: int = None) -> str:
        '''
        Converts ICD codes to PheWAS codes.

        Args:
            icd_code: str - The ICD code to convert.
            icd_type: int - The type of ICD code (9 for ICD-9, 10 for ICD-10).

        Returns:
            str: The PheWAS code with prefix 'phe_', or the original ICD code with respective prefix if conversion fails.
        '''
        assert (icd_type is not None) and (icd_type in [9, 10]), 'icd_type parameter must be either 9 or 10'

        if icd_type == 9:
            try:
                return 'phe_' + str(self.icd9_phe_dict_v2[icd_code])
            except KeyError:
                try:
                    return 'phe_' + str(self.icd9_phe_dict_v1[icd_code])
                except KeyError:
                    icd_10_cm = self.standardize_elements_icd10(icd_type, icd_code)
                    if icd_10_cm.startswith('ICD9CM:'):
                        return icd_10_cm
                    else:
                        icd10_code = icd_10_cm[7:]
                        return 'phe_' + str(self.icd10_phe_dict.get(icd10_code, 'ICD9CM:' + icd_code))
        elif icd_type == 10:
            return 'phe_' + str(self.icd10_phe_dict.get(icd_code, 'ICD10CM:' + icd_code))