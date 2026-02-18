"""
Simple DAPI fluorescence image segmentation workflow.
"""

import argparse
import numpy as np
from skimage import io, filters, morphology, measure
from skimage.util import img_as_float
from scipy import ndimage as ndi
from pathlib import Path


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="DAPI nucleus segmentation pipeline")
    parser.add_argument("image_path", help="Path to input DAPI image")
    parser.add_argument("result_path", help="Output folder for results")
    parser.add_argument("--sigma", type=float, default=2.0, help="Gaussian blur sigma (default: 2.0)")
    parser.add_argument("--max_size", type=int, default=200, help="Max nucleus area to remove (removes objects ≤ this size, default: 200)")
    parser.add_argument("--closing_radius", type=int, default=3, help="Morphological closing radius (default: 3)")
    return parser.parse_args()


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
    Close gaps, fill holes, remove debris, and label connected nuclei.
    """
    closed_img = morphology.closing(binary_image, morphology.disk(closing_radius))
    filled_img = ndi.binary_fill_holes(closed_img)
    cleaned_img = morphology.remove_small_objects(filled_img, max_size=max_size)
    labeled_img = measure.label(cleaned_img)
    return cleaned_img, labeled_img


def main(image_path, result_path, sigma=2.0, max_size=200, closing_radius=3):
    """
    Run the full segmentation pipeline and save resulting label masks.
    """
    # Load image and run preprocessing, segmentation and then postprocessing.
    raw_img = io.imread(image_path, as_gray=True)
    preprocessed_img = preprocess(raw_img, sigma=sigma)
    binary_img = segment(preprocessed_img)
    cleaned_img, labeled_img = postprocess(binary_img, max_size=max_size, closing_radius=closing_radius)

    # Count and print the number of detected nuclei.
    props = measure.regionprops(labeled_img, intensity_image=raw_img)
    print(f"Nuclei detected: {len(props)}")

    # Save resulting label masks to the specified result folder.
    result_path = Path(result_path)
    result_path.mkdir(parents=True, exist_ok=True)
    file_path = result_path / "labels.tif"
    io.imsave(file_path, labeled_img.astype(np.uint16))

    return labeled_img, props


if __name__ == "__main__":
    args = parse_args()
    main(image_path=args.image_path,
         result_path=args.result_path,
         sigma=args.sigma,
         max_size=args.max_size,
         closing_radius=args.closing_radius)
