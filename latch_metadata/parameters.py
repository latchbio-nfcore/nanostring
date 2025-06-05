import typing
from dataclasses import dataclass
from enum import Enum

import typing_extensions
from flytekit.core.annotation import FlyteAnnotation
from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile
from latch.types.metadata import (
    Fork,
    ForkBranch,
    LatchAuthor,
    LatchRule,
    NextflowMetadata,
    NextflowParameter,
    NextflowRuntimeResources,
    Params,
    Section,
    Spoiler,
    Text,
)

# Import these into your `__init__.py` file:
#
# from .parameters import generated_parameters
flow = [
    Section(
        "Samples",
        Params(
            "input",
        ),
    ),
    Section(
        "Normalization Options",
        Params("normalization_method"),
        Text("- GEO: Geometric Mean \n- GLM: Generalized Linear Model"),
    ),
    Section(
        "Gene Score Options",
        Params("gene_score_yaml"),
        Params("gene_score_method"),
        Text(
            "plage.dir (directed PLAGE). The recommendation is to use PLAGE or PLAGE in the directed form (default) for Nanostring nCounter data."
        ),
    ),
    Section(
        "Output Directory",
        Params("run_name"),
        Text("Parent directory for outputs"),
        Params("outdir"),
    ),
    Spoiler(
        "Optional Arguments",
        Text("Additional optional arguments"),
        Spoiler(
            "General Options",
            Params("multiqc_title", "heatmap_id_column", "multiqc_methods_description"),
        ),
        Spoiler(
            "Skipping Options",
            Params("skip_heatmap"),
        ),
    ),
]


@dataclass(frozen=True)
class Sample:
    RCC_FILE: LatchFile
    RCC_FILE_NAME: str
    SAMPLE_ID: str


class normalization_method(Enum):
    geo = "GEO"
    glm = "GLM"


class gene_score_method(Enum):
    plage = "plage"
    plage_dir = "plage.dir"
    gsva = "GSVA"
    singscore = "singscore"
    ssgsea = "ssgsea"
    median = "median"
    mean = "mean"
    sams = "sams"


generated_parameters = {
    "input": NextflowParameter(
        type=typing.List[Sample],
        display_name="Samplesheet",
        samplesheet=True,
        samplesheet_type="csv",
        description="Path to comma-separated file containing information about the samples in the experiment.",
    ),
    "outdir": NextflowParameter(
        type=typing_extensions.Annotated[LatchDir, FlyteAnnotation({"output": True})],
        display_name="Output Directory",
        default=None,
        section_title=None,
        description="The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure.",
    ),
    "run_name": NextflowParameter(
        type=str,
        display_name="Run Name",
        default=None,
        section_title=None,
        description="Name of the run. The output will be saved in a folder with this name.",
    ),
    "multiqc_title": NextflowParameter(
        type=typing.Optional[str],
        display_name="MultiQC Title",
        section_title=None,
        description="MultiQC report title. Printed as page header, used for filename if not otherwise specified.",
    ),
    "heatmap_id_column": NextflowParameter(
        type=typing.Optional[str],
        display_name="Heatmap ID Column",
        default="SAMPLE_ID",
        description="The column used for heatmap generation, specifying the rows. The values in this column have to be unique.",
    ),
    "heatmap_genes_to_filter": NextflowParameter(
        type=typing.Optional[LatchFile],
        display_name="Genes to Visualize",
        default=None,
        section_title=None,
        description="Path to YAML file (list, one item per line) to specify which genes should be used for the gene-count heatmap.",
    ),
    "normalization_method": NextflowParameter(
        type=normalization_method,
        display_name="Normalization Method",
        default=normalization_method.geo,
        description="The method to use for normalization of nCounter data.",
    ),
    "gene_score_method": NextflowParameter(
        type=gene_score_method,
        display_name="Gene Score Computation",
        default=gene_score_method.plage_dir,
        description="This selects the algorithm for computing the respective gene score. Default is 'plage.dir'.",
    ),
    "gene_score_yaml": NextflowParameter(
        type=typing.Optional[LatchFile],
        display_name="Gene Sets",
        default=None,
        section_title=None,
        description="This sets the YAML to be used for computing the gene scores. Needs both a name for each set of genes and respective genes to be selected.",
    ),
    "skip_heatmap": NextflowParameter(
        type=bool,
        display_name="Skip Heatmap",
        default=None,
        description="Skip creating the heatmap",
    ),
    "multiqc_methods_description": NextflowParameter(
        type=typing.Optional[str],
        display_name="Custom MultiQC",
        default=None,
        description="Custom MultiQC yaml file containing HTML including a methods description.",
    ),
}
