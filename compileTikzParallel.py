import os
import subprocess
import time
import argparse
from typing import List

def mirror_directory_structure(src_root: str, out_root: str):
    """
    Mirror the folder structure from src_root into out_root.
    Only creates directories if they don't already exist.
    """
    # --- Check if src_root exists ---
    if not os.path.exists(src_root):
        raise FileNotFoundError(f"Source directory does not exist: {src_root}")

    # --- Check if src_root is empty ---
    if not any(os.scandir(src_root)):
        raise FileNotFoundError(f"Source directory is empty: {src_root}")

    for dirpath, _, _ in os.walk(src_root):
        # Construct relative path from the src root
        rel_path = os.path.relpath(dirpath, src_root)
        target_path = os.path.join(out_root, rel_path)

        if not os.path.exists(target_path):
            os.makedirs(target_path)
            print(f"Created directory: {target_path}")
        else:
            print(f"Directory already exists: {target_path}")


def find_outdated_tex_files(src_root: str, out_root: str) -> List[tuple]:
    """
    Find .tex files in src_root whose corresponding PDFs in out_root are missing or outdated.
    Return a list of (tex_path, pdf_output_dir) tuples.
    """
    tex_jobs = []
    for dirpath, _, filenames in os.walk(src_root):
        for filename in filenames:
            if filename.endswith(".tex"):
                tex_path = os.path.join(dirpath, filename)
                rel_dir = os.path.relpath(dirpath, src_root)
                pdf_dir = os.path.join(out_root, rel_dir)
                pdf_path = os.path.join(pdf_dir, filename.replace(".tex", ".pdf"))

                if not os.path.exists(pdf_path) or os.path.getmtime(tex_path) > os.path.getmtime(pdf_path):
                    tex_jobs.append((tex_path, pdf_dir))
    return tex_jobs

def run_parallel_lualatex(jobs: List[tuple], max_threads: int):
    """
    Use GNU parallel to compile tex files with lualatex in parallel.
    """
    if not jobs:
        print("No .tex files need recompilation.")
        return

    print(f"Found {len(jobs)} .tex file(s) to compile. Launching parallel compilation with maximum allowed {max_threads} threads.")

    # Create command list for GNU parallel
    commands = [
        f"TEXINPUTS={src_root}: lualatex -halt-on-error -interaction=batchmode -output-directory='{pdf_dir}' '{tex_path}' > /dev/null"
        for tex_path, pdf_dir in jobs
    ]

    # Write commands to temporary file
    with open("tmp_compile_jobs.txt", "w") as f:
        for cmd in commands:
            f.write(cmd + "\n")

    # Run them using parallel
    subprocess.run(
        ["parallel", "-j", str(max_threads), "::::", f"tmp_compile_jobs.txt"],
        check=True
    )

    # Clean up
    os.remove("tmp_compile_jobs.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compile standalone TikZ figures in parallel"
    )

    # Positional arguments
    parser.add_argument(
        "src_root",
        type=str,
        help="Root directory containing standalone TikZ (.tex) files"
    )

    parser.add_argument(
        "out_root",
        type=str,
        help="Output directory for compiled PDF files"
    )

    # Optional arguments
    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=32,
        help="Maximum number of parallel jobs (default: 32)"
    )

    args = parser.parse_args()

    # Normalize paths
    src_root = os.path.abspath(args.src_root)
    out_root = os.path.abspath(args.out_root)
    max_parallel_jobs = args.jobs

    # Sanity checks
    if not os.path.isdir(src_root):
        print(f"Error: source directory does not exist: {src_root}")
        exit(1)

    # Create output root if necessary
    os.makedirs(out_root, exist_ok=True)

    print(f"Source directory : {src_root}")
    print(f"Output directory : {out_root}")
    print(f"Parallel jobs    : {max_parallel_jobs}")

    print("\n=== Step 1: Mirroring directory structure ===")
    mirror_directory_structure(src_root, out_root)
    print("Done.")

    print("\n=== Step 2: Detecting outdated .tex files ===")
    tex_jobs = find_outdated_tex_files(src_root, out_root)

    for tex_path, _ in tex_jobs:
        print(f"Needs compile: {tex_path}")

    if not tex_jobs:
        print("No files need recompilation.")
        exit(0)

    start_time = time.time()
    run_parallel_lualatex(tex_jobs, max_parallel_jobs)
    elapsed_time = time.time() - start_time

    print("\nCompilation finished.")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
