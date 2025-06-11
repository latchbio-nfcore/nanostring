import csv
import os
import shutil
import subprocess
import sys
import typing
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional

import requests
import typing_extensions
from flytekit.core.annotation import FlyteAnnotation
from latch.executions import rename_current_execution, report_nextflow_used_storage
from latch.ldata.path import LPath
from latch.resources.tasks import custom_task, nextflow_runtime_task, small_task
from latch.resources.workflow import workflow
from latch.types import metadata
from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile
from latch_cli.nextflow.utils import _get_execution_name
from latch_cli.nextflow.workflow import get_flag
from latch_cli.services.register.utils import import_module_by_path
from latch_cli.utils import urljoins

from latch_metadata.parameters import gene_score_method, normalization_method

meta = Path("latch_metadata") / "__init__.py"
import_module_by_path(meta)
import latch_metadata


@custom_task(cpu=0.25, memory=0.5, storage_gib=1)
def initialize(run_name: str) -> str:
    rename_current_execution(str(run_name))

    token = os.environ.get("FLYTE_INTERNAL_EXECUTION_ID")
    if token is None:
        raise RuntimeError("failed to get execution token")

    headers = {"Authorization": f"Latch-Execution-Token {token}"}

    print("Provisioning shared storage volume... ", end="")
    resp = requests.post(
        "http://nf-dispatcher-service.flyte.svc.cluster.local/provision-storage-ofs",
        headers=headers,
        json={
            "storage_expiration_hours": 168,
            "version": 2,
        },
    )
    resp.raise_for_status()
    print("Done.")

    return resp.json()["name"]


@dataclass
class Sample:
    RCC_FILE: LatchFile
    RCC_FILE_NAME: str
    SAMPLE_ID: str
    TREATMENT: typing.Optional[str] = None
    SOURCE: typing.Optional[str] = None
    OTHER_METADATA: typing.Optional[str] = None


@small_task
def custom_samplesheet_constructor(
    samples: List[Sample], outdir: LatchOutputDir, run_name: str
) -> LatchFile:
    samplesheet = Path("/root/samplesheet.csv")
    columns = [
        "RCC_FILE",
        "RCC_FILE_NAME",
        "SAMPLE_ID",
        "TREATMENT",
        "SOURCE",
        "OTHER_METADATA",
    ]

    with open(samplesheet, "w") as f:
        writer = csv.DictWriter(f, columns, delimiter=",")
        writer.writeheader()
        for sample in samples:
            writer.writerow(
                {
                    "RCC_FILE": sample.RCC_FILE.remote_path,
                    "RCC_FILE_NAME": sample.RCC_FILE_NAME,
                    "SAMPLE_ID": sample.SAMPLE_ID,
                    "TREATMENT": sample.TREATMENT,
                    "SOURCE": sample.SOURCE,
                    "OTHER_METADATA": sample.OTHER_METADATA,
                }
            )

    return LatchFile(
        str(samplesheet), remote_path=f"{outdir.remote_path}/{run_name}/samplesheet.csv"
    )


# input_construct_samplesheet = metadata._nextflow_metadata.parameters[
#     "input"
# ].samplesheet_constructor


@nextflow_runtime_task(cpu=4, memory=8, storage_gib=100)
def nextflow_runtime(
    pvc_name: str,
    input: typing.List[Sample],
    run_name: str,
    outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({"output": True})],
    multiqc_title: typing.Optional[str],
    heatmap_genes_to_filter: typing.Optional[LatchFile],
    gene_score_yaml: typing.Optional[LatchFile],
    skip_heatmap: typing.Optional[bool],
    genome: typing.Optional[str],
    multiqc_methods_description: typing.Optional[str],
    heatmap_id_column: typing.Optional[str],
    normalization_method: normalization_method,
    gene_score_method: gene_score_method,
) -> None:
    root_dir = Path("/root")
    shared_dir = Path("/nf-workdir")

    exec_name = _get_execution_name()
    if exec_name is None:
        print("Failed to get execution name.")
        exec_name = "unknown"

    latch_log_dir = urljoins("latch:///nanostring/nf_nf_core_nanostring", exec_name)
    print(f"Log directory: {latch_log_dir}")

    input_samplesheet = custom_samplesheet_constructor(
        samples=input, run_name=run_name, outdir=outdir
    )

    to_ignore = {
        "latch",
        ".latch",
        ".git",
        "nextflow",
        ".nextflow",
        "work",
        "results",
        "miniconda",
        "anaconda3",
        "mambaforge",
    }

    for p in root_dir.iterdir():
        if p.name in to_ignore:
            continue

        src = root_dir / p.name
        target = shared_dir / p.name

        if p.is_dir():
            shutil.copytree(
                src,
                target,
                ignore_dangling_symlinks=True,
                dirs_exist_ok=True,
            )
        else:
            shutil.copy2(src, target)

    profile_list = ["docker", "test"]
    if False:
        profile_list.extend([p.value for p in execution_profiles])

    if len(profile_list) == 0:
        profile_list.append("standard")

    profiles = ",".join(profile_list)

    cmd = [
        "/root/nextflow",
        "run",
        str(shared_dir / "main.nf"),
        "-work-dir",
        str(shared_dir),
        "-profile",
        profiles,
        "-c",
        "latch.config",
        "-resume",
        *get_flag("input", input_samplesheet),
        *get_flag("outdir", LatchOutputDir(f"{outdir.remote_path}/{run_name}")),
        *get_flag("multiqc_title", multiqc_title),
        *get_flag("heatmap_id_column", heatmap_id_column),
        *get_flag("heatmap_genes_to_filter", heatmap_genes_to_filter),
        *get_flag("normalization_method", normalization_method),
        *get_flag("gene_score_method", gene_score_method),
        *get_flag("gene_score_yaml", gene_score_yaml),
        *get_flag("skip_heatmap", skip_heatmap),
        *get_flag("genome", genome),
        *get_flag("multiqc_methods_description", multiqc_methods_description),
    ]

    print("Launching Nextflow Runtime")
    print(" ".join(cmd))
    print(flush=True)

    failed = False
    try:
        env = {
            **os.environ,
            "NXF_ANSI_LOG": "false",
            "NXF_HOME": "/root/.nextflow",
            "NXF_OPTS": "-Xms1536M -Xmx6144M -XX:ActiveProcessorCount=4",
            "NXF_DISABLE_CHECK_LATEST": "true",
            "NXF_ENABLE_VIRTUAL_THREADS": "false",
            "NXF_ENABLE_FS_SYNC": "true",
        }

        if False:
            env["LATCH_LOG_DIR"] = latch_log_dir

        subprocess.run(
            cmd,
            env=env,
            check=True,
            cwd=str(shared_dir),
        )
    except subprocess.CalledProcessError:
        failed = True
    finally:
        print()

        nextflow_log = shared_dir / ".nextflow.log"
        if nextflow_log.exists():
            remote = LPath(urljoins(latch_log_dir, "nextflow.log"))
            print(f"Uploading .nextflow.log to {remote.path}")
            remote.upload_from(nextflow_log)

        print("Computing size of workdir... ", end="")
        try:
            result = subprocess.run(
                ["du", "-sb", str(shared_dir)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5 * 60,
            )

            size = int(result.stdout.split()[0])
            report_nextflow_used_storage(size)
            print(f"Done. Workdir size: {size / 1024 / 1024 / 1024: .2f} GiB")
        except subprocess.TimeoutExpired:
            print(
                "Failed to compute storage size: Operation timed out after 5 minutes."
            )
        except subprocess.CalledProcessError as e:
            print(f"Failed to compute storage size: {e.stderr}")
        except Exception as e:
            print(f"Failed to compute storage size: {e}")

    if failed:
        sys.exit(1)


@workflow(metadata._nextflow_metadata)
def nf_nf_core_nanostring(
    input: typing.List[Sample],
    run_name: str,
    outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({"output": True})],
    multiqc_title: typing.Optional[str],
    heatmap_genes_to_filter: typing.Optional[LatchFile],
    gene_score_yaml: typing.Optional[LatchFile],
    skip_heatmap: bool,
    genome: typing.Optional[str],
    multiqc_methods_description: typing.Optional[str],
    heatmap_id_column: typing.Optional[str] = "SAMPLE_ID",
    normalization_method: normalization_method = normalization_method.geo,
    gene_score_method: gene_score_method = gene_score_method.plage_dir,
) -> None:
    """
    nf-core/nanostring** is a bioinformatics pipeline that can be used to analyze NanoString data. The performed analysis steps include quality control and data normalization.
    """
    pvc_name: str = initialize(run_name=run_name)
    nextflow_runtime(
        pvc_name=pvc_name,
        run_name=run_name,
        input=input,
        outdir=outdir,
        multiqc_title=multiqc_title,
        heatmap_id_column=heatmap_id_column,
        heatmap_genes_to_filter=heatmap_genes_to_filter,
        normalization_method=normalization_method,
        gene_score_method=gene_score_method,
        gene_score_yaml=gene_score_yaml,
        skip_heatmap=skip_heatmap,
        genome=genome,
        multiqc_methods_description=multiqc_methods_description,
    )
