
from dataclasses import dataclass
import typing
import typing_extensions

from flytekit.core.annotation import FlyteAnnotation

from latch.types.metadata import NextflowParameter
from latch.types.file import LatchFile
from latch.types.directory import LatchDir, LatchOutputDir

# Import these into your `__init__.py` file:
#
# from .parameters import generated_parameters

generated_parameters = {
    'input': NextflowParameter(
        type=LatchFile,
        default=None,
        section_title='Input/output options',
        description='Path to comma-separated file containing information about the samples in the experiment.',
    ),
    'outdir': NextflowParameter(
        type=typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})],
        default=None,
        section_title=None,
        description='The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure.',
    ),
    'email': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Email address for completion summary.',
    ),
    'multiqc_title': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='MultiQC report title. Printed as page header, used for filename if not otherwise specified.',
    ),
    'heatmap_id_column': NextflowParameter(
        type=typing.Optional[str],
        default='SAMPLE_ID',
        section_title='Processing options',
        description='The column used for heatmap generation, specifying the rows. The values in this column have to be unique.',
    ),
    'heatmap_genes_to_filter': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Path to yml file (list, one item per line) to specify which genes should be used for the gene-count heatmap.',
    ),
    'normalization_method': NextflowParameter(
        type=typing.Optional[str],
        default='GEO',
        section_title='Normalization Parameters',
        description='The method to use for normalization of nCounter data.',
    ),
    'gene_score_method': NextflowParameter(
        type=typing.Optional[str],
        default='PLAGE',
        section_title='Gene Score Computation',
        description="This selects the algorithm for computing the respective gene score. Default is 'PLAGE'.",
    ),
    'gene_score_yaml': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='This sets the YAML to be used for computing the gene scores. Needs both a name for each set of genes and respective genes to be selected.',
    ),
    'skip_heatmap': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title='Skipping Options',
        description='Skip creating the heatmap',
    ),
    'genome': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title='Reference genome options',
        description='Name of iGenomes reference.',
    ),
    'multiqc_methods_description': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title='Generic options',
        description='Custom MultiQC yaml file containing HTML including a methods description.',
    ),
}

