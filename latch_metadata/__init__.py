from pathlib import Path

from latch.types.directory import LatchDir
from latch.types.metadata import LatchAuthor, NextflowMetadata, NextflowRuntimeResources

from .parameters import flow, generated_parameters

NextflowMetadata(
    display_name="nf-core/nanostring",
    about_page_path=Path("README.md"),
    author=LatchAuthor(
        name="LatchBio",
    ),
    parameters=generated_parameters,
    runtime_resources=NextflowRuntimeResources(
        cpus=4,
        memory=8,
        storage_gib=100,
    ),
    log_dir=LatchDir("latch:///nanostring"),
    flow=flow,
)
