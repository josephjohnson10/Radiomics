import pydicom as dicom
import numpy as np
import os
import glob
from skimage import measure
import scipy.ndimage
import csv
from rtutils import RTStructBuilder

def load_scan(path):
    slices = [dicom.read_file(s) for s in glob.glob(path+'/*.dcm')]
    slices.sort(key = lambda x: float(x.ImagePositionPatient[2]))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices

def resample(img, new_spacing=[1,1,1]):
    image = img['array']
    spacing = img['Spacing']
    img_size = np.array(image.shape)
    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor
    image = scipy.ndimage.zoom(image, real_resize_factor)
    return image, img_size, real_resize_factor

def normalize_hu(image):
    MIN_BOUND = -1200.0
    MAX_BOUND = 600.0
    image = (image - MIN_BOUND) / (MAX_BOUND - MIN_BOUND)
    image[image > 1] = 1
    image[image < 0] = 0
    image = (image*255).astype('uint8')
    return image

def crop_roi(resampled_img, img_size, seed_pos, crop_size, resize_factor):
    initial_seed = [seed_pos[0], seed_pos[1], seed_pos[2]]
    trans_seed = initial_seed*resize_factor
    start = []
    end= []
    for i in range(3):
        s = np.floor(trans_seed[i]-(crop_size[i]/2))
        e = np.ceil(trans_seed[i]+(crop_size[i]/2))
        if s<0:
            s = 0
        if e>resampled_img.shape[i]:
            e = resampled_img.shape[i]
        if e-s != crop_size[i]:
            pad = e-s-crop_size[i]
            if s==0:
                e = e-pad
            else:
                s = s+pad
        start.append(int(s))
        end.append(int(e))       
    roi = resampled_img[start[0]:end[0], start[1]:end[1], start[2]:end[2]]      
    return roi

if __name__ == '__main__':
    home_path = 'NSCLC_External_Dataset'
    save_path = './Nodule_crop_NSCLC'
    csv_file_path = 'External_NSCLC_Radiomics.csv'
    
    header = ['Patient_ID', 'Nodule No', 'Image File', 'Mask File', 'Malignancy']
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # In TCIA, files are inside SeriesInstanceUID folders. We need to group by PatientID.
    all_series = glob.glob(os.path.join(home_path, '*'))
    patient_to_ct = {}
    patient_to_rt = {}

    print("Scanning downloaded folders...")
    for series_dir in all_series:
        if not os.path.isdir(series_dir): continue
        dcms = glob.glob(os.path.join(series_dir, '*.dcm'))
        if not dcms: continue
        try:
            dcm = dicom.dcmread(dcms[0], stop_before_pixels=True)
            pid = dcm.PatientID
            mod = dcm.Modality
            if mod == 'CT':
                patient_to_ct[pid] = series_dir
            elif mod == 'RTSTRUCT':
                patient_to_rt[pid] = series_dir
        except:
            pass

    print(f"Found {len(patient_to_ct)} CTs and {len(patient_to_rt)} RTSTRUCTs.")

    for pid in patient_to_ct:
        if pid not in patient_to_rt:
            continue
            
        try:
            ct_dir = patient_to_ct[pid]
            rt_dir = patient_to_rt[pid]
            rt_file = glob.glob(os.path.join(rt_dir, '*.dcm'))[0]

            # 1. Load Mask using rtutils
            rtstruct = RTStructBuilder.create_from(dicom_series_path=ct_dir, rt_struct_path=rt_file)
            
            # Find the correct GTV ROI name
            roi_names = rtstruct.get_roi_names()
            gtv_name = None
            for name in roi_names:
                if 'GTV' in name.upper():
                    gtv_name = name
                    break
            
            if not gtv_name:
                continue

            mask = rtstruct.get_roi_mask_by_name(gtv_name).astype(int)
            
            # 2. Get Nodule Center
            L_mask = measure.label(mask)
            L_props = measure.regionprops(L_mask)
            center_pos = [np.array(props.centroid).astype(int) for props in L_props]
            
            if len(center_pos) == 0:
                continue

            # 3. Load Image exactly as your code does
            dicom_slices = load_scan(ct_dir)
            
            # Validate alignment: rtutils sometimes transposes. Let's make sure shape matches!
            image = [s.pixel_array*int(s.RescaleSlope)+int(s.RescaleIntercept) for s in dicom_slices]
            image = np.array(image).transpose(1, 2, 0)
            
            # Some rtutils versions return (x, y, z), some return (z, y, x).
            # If mask shape doesn't match image shape, we transpose it to match your original script
            if mask.shape != image.shape:
                mask = mask.transpose(1, 2, 0)
                # Recalculate centers just in case
                L_mask = measure.label(mask)
                L_props = measure.regionprops(L_mask)
                center_pos = [np.array(props.centroid).astype(int) for props in L_props]

            slice_loc = np.array([s.ImagePositionPatient[2] for s in dicom_slices]).astype(float)
            spacing = np.array([dicom_slices[0].PixelSpacing[0], 
                                dicom_slices[0].PixelSpacing[1],
                                dicom_slices[0].SliceThickness]).astype(float)

            # 4. Resample
            image_new = {'array': image, 'Spacing': spacing}
            img, img_size, resize_factor = resample(image_new)
            
            mask_new = {'array': mask, 'Spacing': spacing}
            label, label_size, _ = resample(mask_new)
            
            img = normalize_hu(img)
            
            Nodule_num = 0
            for pos in center_pos:
                Nodule_num += 1
                seed_pos = [pos[0], pos[1], pos[2]]
                
                ROI = crop_roi(img, img_size, seed_pos, [64,64,64], resize_factor)
                ROI_label = crop_roi(label, label_size, seed_pos, [64,64,64], resize_factor)
                
                ROI = (ROI.astype(np.float32)-128)/128
                
                patient_save_path = os.path.join(save_path, pid)
                if not os.path.exists(patient_save_path):
                    os.makedirs(patient_save_path)
                    
                roi_path = os.path.join(patient_save_path, f"{pid}_{Nodule_num}_roi.npy")
                mask_path = os.path.join(patient_save_path, f"{pid}_{Nodule_num}_label.npy")
                
                np.save(roi_path, ROI)
                np.save(mask_path, ROI_label)
                
                data = [pid, Nodule_num, roi_path, mask_path, None]
                with open(csv_file_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(data)
            print(f"Processed Patient {pid} Successfully!")
            
        except Exception as e:
            print(f"Error on {pid}: {e}")

