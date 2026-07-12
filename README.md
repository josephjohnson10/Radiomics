# Radiomics — Lung Cancer Identification from CT Images Using a Multimodal 2.5D Vision Transformer Ensemble

## Overview
This repository contains the complete implementation of a novel Multimodal Ensemble for pulmonary nodule malignancy classification. The method fuses hand-crafted radiomic features (PyRadiomics) with deep semantic embeddings from the pre-trained medical Vision Transformer **microsoft/rad-dino** in a 2.5D multi-slice paradigm.

## Results on LIDC-IDRI (N=1,393 nodules)
| Metric | Score |
|--------|-------|
| AUC | **0.9902** |
| Accuracy | **97.11%** |
| Sensitivity | **90.28%** |
| Specificity | **99.37%** |
| Precision | **97.92%** |
| F1-Score | **93.94%** |

## Repository Structure
```
├── script.ipynb                        # Main training & evaluation notebook
├── Preprocessing_ROI_generator.py      # DICOM preprocessing & nodule extraction
├── Preprocessing_method_initial.py     # Initial preprocessing exploration
├── params.yaml                         # PyRadiomics feature extraction config
├── requirements.txt                    # Python package dependencies
├── Radiomics_Features_Base.csv         # Extracted radiomic features (1,393 nodules)
├── Proposed_Multimodal_Ensemble.pkl    # Saved best model
├── Performance Matrics/                # Results and evaluation outputs
├── models/                             # Pre-trained ViT fold weights
└── Nodule_crop/                        # 3D nodule volumes (not tracked by git)
```

## Dataset
This project uses the publicly available **LIDC-IDRI** dataset:
- 1,018 CT scans from 1,010 patients
- 1,393 nodules after preprocessing (346 malignant, 1,047 benign)
- Available at: https://www.cancerimagingarchive.net

## Installation
```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Preprocess DICOM CT Scans
```bash
python Preprocessing_ROI_generator.py
```
This extracts 64×64×64 nodule crops from raw LIDC-IDRI DICOM files.

### Step 2: Run the Training Pipeline
Open and run `script.ipynb` in Jupyter Notebook or JupyterLab.

The notebook:
1. Loads radiomic features from `Radiomics_Features_Base.csv`
2. Extracts 768-dim ViT embeddings from 5 anchor depth slices per nodule
3. Fuses ViT + radiomic features into a 2,115-dim vector
4. Trains XGBoost + LightGBM ensemble via Stratified 5-Fold Cross-Validation
5. Saves the best model to `Proposed_Multimodal_Ensemble.pkl`

## Method
- **2.5D Multi-Slice ViT**: Five pseudo-RGB images at depths {16, 24, 32, 40, 48} are processed by `microsoft/rad-dino` backbone
- **PyRadiomics**: 1,218 features extracted across Original, LoG (5 sigmas), and Wavelet (8 sub-bands) transformations
- **Ensemble**: XGBoost + LightGBM averaged probability outputs with optimal threshold selection

## Citation
If you use this code, please cite our paper:
> Limna P Das, Jayaraj P B, Joseph Johnson, Seenia Fransis.
> *Radiomics Guided Lung Cancer Identification from CT Images Using a Multimodal 2.5D Vision Transformer Ensemble.*
> 2026.

## License
This project is for academic and research purposes only.
