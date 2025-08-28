# Ai4Health-Helper-Functions

A collection of Python utilities to standardize, map, and convert medical codes and medication identifiers for AI and data science workflows in health data analysis.

---

## Features

- **ICD Code Standardization:**  
  Convert and standardize ICD-9 and ICD-10 codes, map ICD codes to PheWAS (PheCode) codes for phenotype analysis.

- **Medication Standardization:**  
  Convert between RxCUI, ATC, and NDC identifiers, extract active ingredient information, and standardize NDC code formats.

- **Ready for Data Pipelines:**  
  Designed for integration into AI/ML health data pipelines and EHR preprocessing.

---

## Installation

Clone the repository:
```bash
git clone https://github.com/rachac-umass/Ai4Health-Helper-Functions.git
cd Ai4Health-Helper-Functions
```

Install dependencies:
```bash
pip install -r requirements.txt
```
> **Note:**  
> You may need to install additional dependencies such as `pandas`, `polars`, `pyreadr`, `requests`, `numpy`, and `icdmappings`.

---

## Usage

### ICD Code Standardization

See [`Functions/icd_codes_standardizer.py`](Functions/icd_codes_standardizer.py):

```python
from Functions.icd_codes_standardizer import ICDStandardizer

icd = ICDStandardizer()
# Convert ICD-9 to ICD-10
icd10_code = icd.convert_icd9_to_icd10('25000')
# Map ICD-10 to PheWAS code
phewas_code = icd.icd_codes_to_phewas_codes('E11.9', icd_type=10)
```

### Medication Standardization

See [`Functions/medications_standardizer.py`](Functions/medications_standardizer.py):

```python
from Functions.medications_standardizer import standardize_medication

med = standardize_medication()
# Convert RxCUI to ATC
atc_codes = med.convert_rxcui_to_ATC(1049630, ATC_level=4)
# Find active ingredients for RxCUI
ingredients = med.convert_rxcui_to_active_ingrident(1049630)
# Convert 10-digit NDC to 11-digit
ndc_11 = med.ndc_standaradizer_10_to_11_digit('1234-5678-90')
```

---

## File Structure

- `Functions/icd_codes_standardizer.py`  
  ICD code standardization and PheWAS mapping

- `Functions/medications_standardizer.py`  
  Medication code conversion/standardization

- `github_actions_code_check.yaml`  
  GitHub Actions workflow for code checks

---

## Data Requirements

Some operations require mapping files:
- `../Datasets/Phecode_map_v1_2_icd10cm_beta.csv`
- `../Datasets/phecode_map_v1_2_icd9.csv`
- `../Datasets/phemap (1).rda`

These should be downloaded and placed in the `Datasets` directory as shown.

---

## Contributing

Pull requests and issues are welcome! Please open an issue to discuss major changes before PRs.
---

## Acknowledgements

- [PheWAS Catalog](https://phewascatalog.org/)
- [RxNav API](https://rxnav.nlm.nih.gov/)
- [icdmappings Python package](https://pypi.org/project/icd-mappings/])


## To-Do(s)
- Create workflow actions to test functionalities
