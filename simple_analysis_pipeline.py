"""
Simple DAPI fluorescence image segmentation workflow for BIAFLOWS.
"""
import os
import argparse
import numpy as np
from skimage import io, filters, morphology, measure
from skimage.util import img_as_float
from skimage.segmentation import watershed
from skimage.feature import peak_local_max
from scipy import ndimage as ndi


def preprocess(image, sigma=2.0):
    """
    Apply Gaussian smoothing.
    """
    img = img_as_float(image)
    smoothed_img = filters.gaussian(img, sigma=sigma)
    return smoothed_img


def segment(image):
    """
    Binarise image using Otsu thresholding.
    """
    threshold = filters.threshold_otsu(image)
    binary_img = image > threshold
    return binary_img


def postprocess(binary_image, max_size=200, closing_radius=3):
    """
    Close gaps, fill holes, remove debris, apply watershed to separate touching nuclei
    and label connected nuclei.
    """
    # Morphological closing and hole filling
    closed_img = morphology.closing(binary_image, morphology.disk(closing_radius))
    filled_img = ndi.binary_fill_holes(closed_img)
    cleaned_img = morphology.remove_small_objects(filled_img, max_size=max_size)

    # Watershed segmentation to separate touching nuclei
    # 1. Calculate distance transform
    distance = ndi.distance_transform_edt(cleaned_img)

    # 2. Find local maxima (seeds for watershed)
    coords = peak_local_max(distance, footprint=np.ones((3, 3)), labels=cleaned_img)
    mask = np.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    markers = measure.label(mask)

    # 3. Apply watershed
    labeled_img = watershed(-distance, markers, mask=cleaned_img)

    return cleaned_img, labeled_img


def process_single_image(image_path, output_path, sigma=2.0, max_size=200, closing_radius=3):
    """
    Process a single image and save the resulting label mask.
    """
    # Load image and run preprocessing, segmentation and then postprocessing.
    raw_img = io.imread(image_path, as_gray=True)
    preprocessed_img = preprocess(raw_img, sigma=sigma)
    binary_img = segment(preprocessed_img)
    cleaned_img, labeled_img = postprocess(binary_img, max_size=max_size, closing_radius=closing_radius)

    # Count and print the number of detected nuclei.
    props = measure.regionprops(labeled_img, intensity_image=raw_img)
    print(f"Nuclei detected: {len(props)}")

    # Save resulting label mask to the specified result folder & return results
    io.imsave(output_path, labeled_img.astype(np.uint16))
    return labeled_img, props


def run_analysis(in_path, out_path, sigma=2.0, max_size=200, closing_radius=3):
    """
    Process all images in in_path folder and save results to out_path folder.
    """
    # Create output folder if it doesn't exist
    os.makedirs(out_path, exist_ok=True)
    
    # Find all image files in input folder (all files, let scikit-image handle compatibility)
    all_files = os.listdir(in_path)
    print(f"Found {len(all_files)} files to process")
    
    results = []
    for img_filename in all_files:
        print(f"Processing: {img_filename}")
        
        input_path = os.path.join(in_path, img_filename)
        output_path = os.path.join(out_path, img_filename)
        
        try:
            labeled_img, props = process_single_image(
                input_path, output_path, 
                sigma=sigma, 
                max_size=max_size, 
                closing_radius=closing_radius
            )
            results.append({
                'filename': img_filename,
                'labeled_img': labeled_img,
                'props': props
            })
        except Exception as e:
            print(f"  -> Skipping {img_filename}: {e}")
    
    print(f"\nSuccessfully processed {len(results)} images")
    return results


def main():
    """
    Main function for standalone usage with command-line arguments.
    """
    parser = argparse.ArgumentParser(description="DAPI nucleus segmentation pipeline")
    parser.add_argument("in_path", help="Input folder containing DAPI images")
    parser.add_argument("out_path", help="Output folder for resulting label masks")
    parser.add_argument("--sigma", type=float, default=2.0, help="Gaussian blur sigma (default: 2.0)")
    parser.add_argument("--max_size", type=int, default=200, help="Max nucleus area to remove (removes objects ≤ this size, default: 200)")
    parser.add_argument("--closing_radius", type=int, default=3, help="Morphological closing radius (default: 3)")
    args = parser.parse_args()
    
    run_analysis(
        in_path=args.in_path,
        out_path=args.out_path,
        sigma=args.sigma,
        max_size=args.max_size,
        closing_radius=args.closing_radius
    )


if __name__ == "__main__":
    main()
