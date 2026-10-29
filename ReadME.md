# BreastDCEDL

**A Unified, Multi-Site DCE-MRI Dataset for Pathological Complete Response (pCR) Prediction**


---

## Overview

Breast cancer accounts for roughly 12% of all new cancer cases diagnosed globally each year. Early and accurate prediction of treatment response is critical for personalized oncology, enabling clinicians to identify patients likely to achieve a pathological complete response (pCR) after neoadjuvant chemotherapy (NAC), spare non-responders from toxic side effects, and guide surgical planning.

Dynamic Contrast-Enhanced MRI (DCE-MRI) is the gold-standard imaging modality for breast tumor assessment, capturing the kinetics of gadolinium contrast agent uptake across multiple time points. However, heterogeneity across acquisition protocols, scanner vendors, and institutional pipelines has historically fragmented this data into incompatible silos, limiting the generalizability of predictive models.

**BreastDCEDL** addresses this gap by harmonizing data from three major clinical trials — **I-SPY 1**, **I-SPY 2**, and the **Duke Breast Cancer MRI dataset** — into a single standardized repository of over 2,000 patient studies, along with curated metadata, NIfTI-format imaging data, and a complete deep learning pipeline including a fine-tuned Vision Transformer (ViT) model for pCR prediction.

## Aim & Objectives

**Primary Aim:** Construct and publicly release a comprehensive, harmonized benchmark dataset of breast DCE-MRI studies from multiple clinical sources, and demonstrate state-of-the-art pCR prediction using modern deep learning architectures.

**Objectives:**

- Aggregate and standardize DCE-MRI imaging data from I-SPY 1, I-SPY 2, and Duke into a common NIfTI format with consistent naming conventions.
- Curate rich patient-level metadata — receptor status (HR, HER2), tumor volume, imaging geometry, menopause status, and race — for 2,070+ studies.
- Define and compute tumor bounding boxes (`mask_start`/`mask_end`, `sraw`/`eraw`, `scol`/`ecol`) to enable reproducible ROI-centred cropping across datasets.
- Provide ready-to-run Jupyter notebooks for data exploration, visualization, and model inference, compatible with local and Google Colab environments.
- Fine-tune a Vision Transformer (ViT-MAE-Base) on the harmonized dataset for binary pCR classification, with model weights released via Zenodo.
- Provide a minimal cropped variant (`BreastDCEDL_min_crop`) that reduces storage and I/O requirements while preserving tumor context.
- Enable reproducible benchmarking through predefined train/test splits embedded in the metadata.

## Datasets Used

| Dataset | Source | Patients | Notes |
|---|---|---|---|
| I-SPY 1 | TCIA / ACRIN | ~230 | Multi-timepoint DCE-MRI, pCR label |
| I-SPY 2 (ACRIN-6698) | TCIA | ~987 | Adaptive trial, multiple receptor subtypes |
| Duke Breast Cancer MRI | TCIA | ~922 | Single-site, high-resolution |

- **I-SPY 1** enrolled women with stage II/III breast cancer undergoing neoadjuvant chemotherapy at multiple US academic centers from 2002–2006. Imaging was acquired pre-treatment and after cycles 1, 3, and 4 of chemotherapy. Patient IDs follow the `ISPY1_XXXX` convention.
- **I-SPY 2 / ACRIN-6698** is the largest component of BreastDCEDL, contributing ~987 studies with IDs formatted as `ACRIN-6698-XXXXXX` or `ISPY2-XXXXXX`. Receptor status and pCR labels are available for all subjects.
- **Duke Breast Cancer MRI** contains high-resolution imaging from 922 biopsy-confirmed invasive breast cancer patients scanned between 2000–2014 at a single institution, with IDs following the `Breast_MRI_XXX` pattern.

### Combined Statistics

| Statistic | Value |
|---|---|
| Total patients (full metadata) | 2,070 |
| Total patients (min_crop metadata) | 2,072 |
| Datasets merged | I-SPY 1 (spy1), I-SPY 2 (spy2), Duke (duke) |
| Imaging modality | DCE-MRI — NIfTI (.nii.gz) |
| Typical image size (n_xy) | 256 x 256 pixels |
| Typical z-slices (n_z) | 25 – 80 slices |
| Temporal acquisitions (n_times) | 3 – 8 time points |
| Outcome label | pCR: 0 / 1 |
| Receptor subtypes | Triple Negative, HER2+, HR+/HER2− |
| Train / test split | Embedded in metadata (`test` column: 0.0 / 1.0) |

## Metadata Schema

Two metadata CSV files are provided: `BreastDCEDL_metadata.csv` (full dataset, 2,070 rows) and `BreastDCEDL_metadata_min_crop.csv` (cropped-volume variant, 2,072 rows) with adjusted z-slice indices. Both share the following columns:

| Column | Type | Description |
|---|---|---|
| pid | str | Unique patient identifier (e.g. `ACRIN-6698-102212`, `ISPY1_1072`) |
| pCR | float | pCR label: 1.0 = pCR, 0.0 = no pCR, NaN = unknown |
| n_xy | float | In-plane image dimension (pixels, typically 256) |
| n_z | float | Number of axial slices in the full volume |
| n_times | float | Number of DCE temporal acquisitions |
| pre | float | Index of the pre-contrast acquisition |
| post_early | float | Index of the early post-contrast acquisition |
| post_late | float | Index of the late post-contrast acquisition |
| slice_thick | float | Slice thickness in mm |
| xy_spacing | float | In-plane pixel spacing in mm |
| mask_start / mask_end | float | First / last z-slice index containing tumor mask |
| sraw / eraw | float | Row (y-axis) bounding box start / end of tumor ROI |
| scol / ecol | float | Column (x-axis) bounding box start / end of tumor ROI |
| tum_vol | float | Tumor volume in mm³ derived from segmentation mask |
| age | float | Patient age at diagnosis |
| menopause | float | Menopausal status: 1.0 = post-menopausal |
| race_white / race_black | float | Race binary indicators |
| HR | float | Hormone receptor status: 1.0 = positive |
| HER2 | float | HER2 receptor status: 1.0 = positive |
| HR_HER2_STATUS | str | Composite subtype string (TripleNeg, HER2pos, HRposHER2neg) |
| TripleNeg / HER2pos / HRposHER2neg | float | One-hot subtype indicators |
| dataset | str | Source dataset code: spy1, spy2, duke |
| test | float | Train/test split: 1.0 = test set |

## System Architecture & Pipeline

The pipeline consists of five modular stages, from raw imaging data ingestion through to pCR prediction.

**Stage 1 — Data Ingestion**
Raw DCE-MRI volumes from TCIA are downloaded in DICOM format and converted to NIfTI (`.nii.gz`) using `dcm2niix`. Files are organized per patient and per acquisition time point. A utility function `_ds_from_pid()` routes each patient to the correct dataset directory based on PID naming conventions.

**Stage 2 — Metadata Curation**
Clinical labels (pCR, receptor status, demographics) are extracted from trial databases and TCIA annotations. Imaging geometry parameters are read from NIfTI headers. Tumor bounding boxes are derived from segmentation masks, and tumor volume is computed by counting mask voxels and multiplying by voxel volume.

**Stage 3 — Preprocessing**
For each patient, three acquisitions (pre, post_early, post_late) are stacked channel-wise as RGB-analogues. Each channel is min-max normalized independently. A `safe_crop_around_roi()` function crops a 224x224 patch centred on the tumor ROI, handling boundary conditions robustly. ImageNet-standard normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) is then applied.

**Stage 4 — Model (ViT-MAE Fine-Tuning)**
The `facebook/vit-mae-base` Vision Transformer is loaded from HuggingFace Transformers, with its classification head replaced for binary pCR prediction. Fine-tuning is performed using the AdamW optimizer on the training split. Trained weights are hosted on Zenodo (DOI: [10.5281/zenodo.15627233](https://zenodo.org/records/15627233)) due to file size limits on GitHub.

**Stage 5 — Inference & Evaluation**
For each test patient, slices centred on the tumor mask midpoint (±2 slices) are processed through the pipeline. The model outputs per-slice pCR probabilities, aggregated to a patient-level prediction. Evaluation metrics include AUC-ROC, precision, recall, and F1, computed via `sklearn.metrics`.

## Key Algorithms & Code

### NIfTI Data Loading

```python
import nibabel as nib, os, re

def read_nifti(path: str) -> np.ndarray:
    return nib.load(path).get_fdata()

def _last_int(path):
    m = re.search(r'(\d+)\.nii\.gz$', path)
    return int(m.group(1)) if m else -1

def get_sorted_nifti_acquisitions(pid):
    ds = _ds_from_pid(pid)  # infer dataset from PID
    data_path = nifti_path[ds]
    ff = sorted([x for x in os.listdir(data_path) if pid in x], key=_last_int)
    return [read_nifti(os.path.join(data_path, f)) for f in ff]

def get_nifti_mask(pid: str):
    ds = _ds_from_pid(pid)
    mpath = mask_path[ds]
    ff = [x for x in os.listdir(mpath) if pid in x]
    return read_nifti(os.path.join(mpath, ff[0])) if ff else None
```

### RGB Fusion of DCE Channels

```python
def minmax(m):
    if m.max() == 0: return m
    return (m - m.min()) / (m.max() - m.min())

def to_rgb(a, b, c):  # a=pre, b=post_early, c=post_late
    return np.stack([minmax(a), minmax(b), minmax(c)], axis=a.ndim)  # shape: (H, W, 3)
```

### ROI-Centred Cropping

```python
def safe_crop_around_roi(img, roi_cx, roi_cy, crop_size=224):
    W, H = img.size
    half = crop_size // 2
    left, top = roi_cx - half, roi_cy - half
    right, bottom = roi_cx + half, roi_cy + half

    # Shift crop if it exceeds image boundaries
    if left < 0: right -= left; left = 0
    if top < 0: bottom -= top; top = 0
    if right > W: left -= (right - W); right = W
    if bottom > H: top -= (bottom - H); bottom = H
    left, top = max(0, left), max(0, top)

    cropped = img.crop((left, top, right, bottom))
    if cropped.size != (crop_size, crop_size):
        cropped = cropped.resize((crop_size, crop_size))
    return cropped
```

### ViT Model Initialization

```python
import torch
from transformers import AutoImageProcessor, ViTForImageClassification

checkpoint = 'facebook/vit-mae-base'
image_processor = AutoImageProcessor.from_pretrained(checkpoint)
model = ViTForImageClassification.from_pretrained(checkpoint)

# Load fine-tuned weights (from Zenodo)
model.load_state_dict(
    torch.load('./transformer_models/breastdcedl_pcr_vit_model_weights.pth'))
model.to(device).eval()
```

### Per-Patient Inference

```python
def predict_patient_images(model, pid, df, transform, device='cuda'):
    row = df[df['pid'] == pid].iloc[0]
    f, l = max(int(row['mask_start']), 0), min(int(row['mask_end']), int(row['n_z']))
    idx = (f + l) // 2  # midpoint slice
    roi_cx = (int(row['scol']) + int(row['ecol'])) // 2
    roi_cy = (int(row['sraw']) + int(row['eraw'])) // 2
    d = ds.get_all_nifti_acquisitions(pid)
    batch = []
    for k in range(max(idx - 2, f), min(idx + 2, l)):
        img = get_jpg_im(pid, d, k)  # 3-channel PIL image
        img_crop = safe_crop_around_roi(img, roi_cx, roi_cy)
        batch.append(transform(img_crop.convert('RGB')))
    if not batch: return []
    with torch.no_grad():
        logits = model(torch.stack(batch).to(device)).logits
    probs = torch.softmax(logits, dim=1)[:, 1]  # pCR class prob
    return probs.cpu().numpy().tolist()
```

## Experiments & Results

### Dataset Statistics

Class distribution in the full metadata (pCR label):

| Split | pCR = 0 (No Response) | pCR = 1 (Complete Response) | Unknown / NaN |
|---|---|---|---|
| Train | ~820 | ~340 | ~500 |
| Test | ~215 | ~85 | ~110 |

### Receptor Subtype Distribution

| Subtype | Approximate Count | % of Cohort |
|---|---|---|
| Triple Negative (TripleNeg) | ~530 | ~25.6% |
| HER2 Positive (HER2pos) | ~310 | ~15.0% |
| HR+/HER2− (HRposHER2neg) | ~750 | ~36.2% |
| Unknown / Mixed | ~480 | ~23.2% |

### Model Performance

The fine-tuned ViT-MAE-Base model was evaluated on the held-out test set:

- Processes 4–5 axial slices per patient, centred on the tumor midpoint.
- Slice-level pCR probabilities are computed via softmax; patient-level prediction is the mean probability.
- Evaluation metrics include AUC-ROC, precision, recall, and F1-score, computed via `sklearn.metrics`.
- Multi-channel RGB fusion (pre + post_early + post_late) provides richer kinetic information compared to single-phase input.
- The minimal cropped variant (`BreastDCEDL_min_crop`) reduces disk I/O by limiting z-slices to the tumor neighborhood while maintaining equivalent model performance.

### Visualization Capabilities

The notebooks provide rich visualization of the 4D DCE data. For each patient, `show_n_images()` renders axial slices at configurable z-indices, and `to_rgb()` creates pseudo-color overlays mapping pre/post_early/post_late to R/G/B channels for inspecting contrast kinetics. Mask overlays highlight tumor extent within the anatomical context.

## Limitations

- Class imbalance between pCR and non-pCR patients requires careful handling (e.g., weighted loss, oversampling) not yet standardized in the released pipeline.
- Acquisition protocol heterogeneity (scanner field strength, contrast agent dose, temporal resolution) across the three source datasets may introduce systematic biases.
- Patient-level prediction from 4–5 slices discards 3D volumetric context available in the full NIfTI volumes.
- Duke dataset tumor masks are synthesized as bounding boxes rather than pixel-level segmentations, limiting mask-based supervision for that cohort.

## Future Work

- 3D Vision Transformers (e.g., ViT-3D, Video-MAE) to exploit full volumetric DCE dynamics.
- Multi-task learning combining pCR prediction with tumor segmentation and receptor subtype classification.
- Federated learning protocols to enable model training without centralizing raw patient data.
- Integration of radiomic features as auxiliary inputs to the ViT, combining handcrafted and learned representations.
- Prospective validation in clinical workflows at partner institutions.
- Extension to longitudinal response monitoring across all available time points.

## References
1.

1. Dosovitskiy, A. et al. (2020). *An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale.* arXiv:2010.11929.
2. He, K. et al. (2021). *Masked Autoencoders Are Scalable Vision Learners.* arXiv:2111.06377.
3. Hylton, N.M. et al. (2012). *Locally Advanced Breast Cancer: MR Imaging for Prediction of Response to Neoadjuvant Chemotherapy — Results from ACRIN 6657/I-SPY TRIAL.* Radiology, 263(3), 663–672.
4. Hylton, N.M. et al. (2016). *Neoadjuvant Chemotherapy for Breast Cancer: Functional Tumor Volume by MR Imaging Predicts Recurrence-free Survival — Results from the ACRIN 6657/CALGB 150007 I-SPY 1 TRIAL.* Radiology, 279(1), 44–55.
5. Saha, A. et al. (2018). *Machine learning-based radiomics model for automated prediction of lesion identification from MR images.* Scientific Data, Duke Breast Cancer MRI Collection, TCIA.
6. Vaswani, A. et al. (2017). *Attention Is All You Need.* NeurIPS 2017.
7. Braman, N. et al. (2021). *Association of Peritumoral Radiomics with Tumor Biology and Pathologic Response to Preoperative Targeted Therapy for HER2 (ERBB2)–Positive Breast Cancer.* JAMA Network Open.
8. McKinney, S.M. et al. (2020). *International evaluation of an AI system for breast cancer screening.* Nature, 577, 89–94.
9. Clark, K. et al. (2013). *The Cancer Imaging Archive (TCIA): Maintaining and Operating a Public Information Repository.* Journal of Digital Imaging, 26(6), 1045–1057.
10. Esserman, L.J. et al. (2012). *Pathologic Complete Response Predicts Recurrence-Free Survival More Effectively by Cancer Subset: Results from the I-SPY 1 TRIAL — CALGB 150007/150012, ACRIN 6657.* Journal of Clinical Oncology, 30(26), 3242.
11. Wolf, T. et al. (2020). *Transformers: State-of-the-Art Natural Language Processing.* EMNLP 2020. (HuggingFace Transformers library).
12. BreastDCEDL - Naomi Fridman
13. BreastDCEDL Zenodo Data: [https://zenodo.org/records/15627232](https://zenodo.org/records/15627232)
14. BreastDCEDL Zenodo Model Weights: [https://zenodo.org/records/15627233](https://zenodo.org/records/15627233)

