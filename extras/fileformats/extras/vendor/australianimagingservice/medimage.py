# Implement 'extras' for the formats defined in
# fileformats.vendor.australianimagingservice.medimage here, see
# https://arcanaframework.github.io/fileformats/developer/extras.html

import shutil
import typing as ty
from pathlib import Path

from fileformats.core import converter
from fileformats.medimage import DicomCollection
from pydra.compose import python

from fileformats.vendor.australianimagingservice.medimage import (
    DicomSample,
)


@converter
@python.define(outputs=["out_file"])  # type: ignore[untyped-decorator]
def SampleDicomDir(
    in_file: DicomCollection,
    out_file: ty.Optional[Path] = None,
) -> DicomSample:
    """Copy a representative image directly from a DICOM directory.

    Packaging invokes the generic ZIP and sample converters from the same
    deidentified source, so the sampled bytes also occur in the archive.
    """
    sample = in_file.contents[0]
    if out_file is None:
        out_file = Path.cwd() / f"{sample.stem}-sample"
    out_file = out_file.absolute()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(sample, out_file)
    return DicomSample(out_file)
