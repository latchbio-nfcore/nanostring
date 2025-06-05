nf-core/nanostring is a bioinformatics pipeline that can be used to analyze NanoString data. The performed analysis steps include quality control and data normalization.

![nf-core/nanostring](https://raw.githubusercontent.com/nf-core/nanostring/1.3.1/docs/images/nf-core-nanostring_logo_light.png)

## Introduction

**nf-core/nanostring** is a bioinformatics pipeline that can be used to analyze NanoString data. The performed analysis steps include quality control and data normalization.

The pipeline is built using [Nextflow](https://www.nextflow.io), a workflow tool to run tasks across multiple compute infrastructures in a very portable manner. It uses Docker/Singularity containers making installation trivial and results highly reproducible. The [Nextflow DSL2](https://www.nextflow.io/docs/latest/dsl2.html) implementation of this pipeline uses one container per process which makes it much easier to maintain and update software dependencies. Where possible, these processes have been submitted to and installed from [nf-core/modules](https://github.com/nf-core/modules) in order to make them available to all nf-core pipelines, and to everyone within the Nextflow community!

## Pipeline summary

1. Quality control with NACHO ([`NACHO`](https://github.com/mcanouil/NACHO/))
2. Perform normalization with NACHO
3. Create count tables with provided metadata
4. Present QC for NanoString data ([`MultiQC`](http://multiqc.info/))

## Pipeline tubemap

![nf-core/nanostring](https://raw.githubusercontent.com/nf-core/nanostring/1.3.1/assets/nf-core_nanostring_tubemap.png)

## Usage

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) on how
> to set-up Nextflow. Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline)
> with `-profile test` before running the workflow on actual data.

First, prepare a samplesheet with your input data that looks as follows:

`samplesheet.csv`:

```csv
RCC_FILE,RCC_FILE_NAME,SAMPLE_ID
/path/to/sample1.RCC,sample1.RCC,sample1
/path/to/sample2.RCC,sample2.RCC,sample2
```

Each row represents a RCC file with counts.

Now, you can run the pipeline using:

```bash
nextflow run nf-core/nanostring \
   -profile <docker/singularity/.../institute> \
   --input samplesheet.csv \
   --outdir <OUTDIR>
```

> [!WARNING]
> Please provide pipeline parameters via the CLI or Nextflow `-params-file` option. Custom config files including those provided by the `-c` Nextflow option can be used to provide any configuration _**except for parameters**_; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

For more details and further functionality, please refer to the [usage documentation](https://nf-co.re/nanostring/usage) and the [parameter documentation](https://nf-co.re/nanostring/parameters).

## Pipeline output

To see the results of an example test run with a full size dataset refer to the [results](https://nf-co.re/nanostring/results) tab on the nf-core website pipeline page.
For more details about the output files and reports, please refer to the
[output documentation](https://nf-co.re/nanostring/output).

## Credits

nf-core/nanostring was originally written by Peltzer, Alexander & Mohr, Christopher. Extensive support was provided from other co-authors on the scientific or technical input required for the pipeline:

- Stadermann, Kai
- Zwick, Matthias
- Leparc, Germán
- Schmid, Ramona

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch on the [Slack `#nanostring` channel](https://nfcore.slack.com/channels/nanostring) (you can join with [this invite](https://nf-co.re/join/slack)).

## Citations

If you use nf-core/nanostring for your analysis, please cite the publication: [nf-core/nanostring Bioinformatics](https://academic.oup.com/bioinformatics/advance-article/doi/10.1093/bioinformatics/btae019/7517109) and the [Zenodo DOI](https://doi.org/10.5281/zenodo.8028303).

An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

You can cite the `nf-core` publication as follows:

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).
