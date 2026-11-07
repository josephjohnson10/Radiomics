# RIM-Former: Radiomics-Integrated Multimodal 2.5D Vision Transformer Framework for Pulmonary Nodule Malignancy-Risk Classification from CT Images

[![Paper: IOP BPEX](https://img.shields.io/badge/Paper-IOP%20BPEX%20(Under%20Review)-blue.svg)](Paper_Minor_Revision/Revised_Manuscript.pdf)
[![Status: Minor Revision](https://img.shields.io/badge/Status-Minor%20Revision%20(R1)-green.svg)](Paper_Minor_Revision/)

## Overview
This repository contains the complete implementation and revision materials for **RIM-Former**, a multimodal framework for pulmonary nodule malignancy risk classification from CT scans. The method fuses quantitative handcrafted radiomic features (PyRadiomics) with deep semantic representations from the pre-trained medical Vision Transformer **`microsoft/rad-dino`** in a 2.5D multi-slice paradigm under a gradient-boosted ensemble head.

## Results on LIDC-IDRI ($N=1{,}393$ nodules)
Evaluated on the full, unfiltered LIDC-IDRI benchmark under patient-level Stratified 5-Fold Cross-Validation (StratifiedGroupKFold, $k=5$, 611 unique patients, retaining all indeterminate Score 3 nodules):

| Metric | Score |
|---|---|
| Area Under the ROC Curve (AUC) | **0.9902** |
| Accuracy | **97.11%** |
| Specificity | **99.37%** |
| Precision (PPV) | **97.92%** |
| Sensitivity (Recall) | **90.28%** |
| F1-Score | **93.94%** |
| External Validation (LNDb Dataset, $N=284$) | **AUC 0.8971, Precision 97.41%** |
| End-to-End Inference Latency | **100.1 ± 7.1 ms / nodule** |

## Repository Structure
```
├── Paper_Minor_Revision/               # Minor revision manuscript, response letter, and submission sources
│   ├── Revised_Manuscript.pdf          # Full compiled revised manuscript (14 pages)
│   ├── Revised_Manuscript.tex          # LaTeX source matching IOP Publishing format
│   ├── Response_to_Reviewers.pdf       # Compiled point-by-point response to reviewers (7 pages)
│   ├── Response_to_Reviewers.docx      # Word version of response with official blue-text styling
│   ├── Source_Files.zip                # Complete verified submission package
│   ├── references.bib                  # BibTeX bibliography
│   └── iopjournal.cls                  # Official IOP journal LaTeX class
├── Performance Matrics/                # Visualizations, diagrams, and TreeSHAP explainability plots
│   ├── SHAP_XGB_Beeswarm.png           # TreeSHAP beeswarm attribution for XGBoost
│   ├── SHAP_LGB_Beeswarm.png           # TreeSHAP beeswarm attribution for LightGBM
│   ├── SHAP_XGB_Bar.png                # Top-20 mean |SHAP| feature importance for XGBoost
│   ├── SHAP_LGB_Bar.png                # Top-20 mean |SHAP| feature importance for LightGBM
│   ├── ViT_Radiomics_Pipeline.png      # End-to-end multimodal pipeline architecture
│   ├── Radiomics_Workflow.png          # PyRadiomics quantitative feature extraction workflow
│   ├── ViT_2.5D_Architecture.png       # 2.5D multi-slice spatial slicing diagram
│   └── Ensemble_Model_Description.png  # Ensemble classifier hyperparameter structure
├── script.ipynb                        # Main training, patient-level CV, & evaluation pipeline
├── SHAP_Analysis.ipynb                 # Post-hoc TreeSHAP interpretability and plotting
├── Preprocessing_ROI_generator.py      # DICOM preprocessing & 3D nodule volume cropping
├── Preprocessing_method_initial.py     # Initial exploratory preprocessing routines
├── params.yaml                         # PyRadiomics feature extraction configuration
├── requirements.txt                    # Python dependencies
├── Radiomics_Features_Base.csv         # 1,218 extracted radiomic features across 1,393 nodules
├── Proposed_Multimodal_Ensemble.pkl    # Serialized calibrated ensemble model weights
├── models/                             # Pre-trained ViT fold weights (tracked via Git LFS)
└── Nodule_crop/                        # Segmented nodule crops (local dataset)
```

## Dataset
This project evaluates on the publicly available **LIDC-IDRI** benchmark:
- 1,018 thoracic CT scans from 1,010 patients
- 1,393 pulmonary nodules (346 malignant, 1,047 benign, fully retaining all 561 ambiguous Score 3 nodules)
- Freely accessible via The Cancer Imaging Archive: https://www.cancerimagingarchive.net

External validation is performed on the independent **LNDb (Lesion Annotated Database)** cohort (284 nodules across 236 CT scans from a European multi-center institution).

## Installation
```bash
pip install -r requirements.txt
```

## Usage

### 1. Preprocess DICOM CT Scans
```bash
python Preprocessing_ROI_generator.py
```
Crops $64\times64\times64$ nodule volumes centered at radiologist coordinates with $[-1000, 1000]$\,HU windowing.

### 2. Run Main Training & Evaluation Pipeline
Open and execute `script.ipynb`:
- Extracts 1,218 IBSI-compliant radiomic features using `params.yaml`.
- Extracts 768-dimensional CLS token embeddings across 5 axial anchor depths using `microsoft/rad-dino`.
- Fuses features into a 1,986-dimensional multimodal vector ($768 + 1{,}218$).
- Trains XGBoost and LightGBM with regularized hyperparameters via strict `StratifiedGroupKFold` cross-validation (preventing patient data leakage).

### 3. TreeSHAP Explainability Analysis
Open and execute `SHAP_Analysis.ipynb`:
- Computes exact Shapley values using `shap.TreeExplainer`.
- Generates beeswarm plots and mean absolute feature importance rankings.

## Citation
If you utilize this repository or findings in your research, please cite:
> Limna P Das, Joseph Johnson, Syam Kumar K S, Seenia Fransis, and Jayaraj P B.
> *RIM-Former: Radiomics-Integrated Multimodal 2.5D Vision Transformer Framework for Pulmonary Nodule Malignancy-Risk Classification from CT Images.*
> Biomedical Physics & Engineering Express (IOP Publishing), Reference: BPEX-106740.R1, 2026.

## License
This project is open-source under the MIT License for academic and non-commercial research purposes.
