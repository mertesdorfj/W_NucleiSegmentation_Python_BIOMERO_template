import sys
import os
from cytomine.models import Job
from biaflows import CLASS_OBJSEG
from biaflows.helpers import BiaflowsJob, prepare_data, upload_data, upload_metrics, get_discipline
from simple_analysis_pipeline import run_analysis


def main(argv):
    base_path = "{}".format(os.getenv("HOME"))  # Mandatory for Singularity

    with BiaflowsJob.from_cli(argv) as bj:      # Create a BiaflowsJob object from CLI args (provides access to images, ground truth, workflow params & output dir)
        problem_cls = get_discipline(bj, default=CLASS_OBJSEG)  # Change following to the actual problem class of the workflow
        bj.job.update(status=Job.RUNNING, progress=0, statusComment="Initialisation...")  # Notify Biaflows about jobstart
        
        ########## 1. Prepare amd preprocess data for workflow ###########################
        in_imgs, gt_imgs, in_path, gt_path, out_path, tmp_path = prepare_data(problem_cls, bj, is_2d=True, **bj.flags)

        ########## 2. Run image analysis workflow (Nuclei segmentation) ##################
        bj.job.update(progress=25, statusComment="Launching nuclei segmentation workflow...")

        # Launch Cellpose via command-line with pretrained nuclei model & selected diameter size
        results = run_analysis(
            in_path=in_path,
            out_path=out_path,
            sigma=bj.parameters.sigma,
            max_size=bj.parameters.max_size,
            closing_radius=bj.parameters.closing_radius
        )

        # Exit with error code 1 in case no valid results were computed
        if not results:
            print("No images were successfully processed, terminate")
            bj.job.update(status=Job.FAILED, progress=100, statusComment="No images processed")
            sys.exit(1)

        ########## 3. Upload data to BIAFLOWS #################################
        bj.job.update(progress=60, statusComment="Uploading results...")
        upload_data(problem_cls, bj, in_imgs, out_path, **bj.flags, monitor_params={
            "start": 60, "end": 90, "period": 0.1,
            "prefix": "Extracting and uploading polygons from masks"})
        
        ########## 4. Compute and upload metrics ##############################
        bj.job.update(progress=90, statusComment="Computing and uploading metrics...")
        upload_metrics(problem_cls, bj, in_imgs, gt_path, out_path, tmp_path, **bj.flags)

        # Mark job as completed in Biaflows
        bj.job.update(progress=100, status=Job.TERMINATED, status_comment="Finished.")


if __name__ == "__main__":
    main(sys.argv[1:])
