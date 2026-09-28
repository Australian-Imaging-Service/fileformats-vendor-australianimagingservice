# Implement 'extras' for the formats defined in
# fileformats.vendor.australianimagingservice.medimage here, see
# https://arcanaframework.github.io/fileformats/developer/extras.html

import shutil
import typing as ty
from pathlib import Path

from fileformats.core import converter
from fileformats.medimage import DicomDir, DicomImage
from pydra.compose import python

from fileformats.vendor.australianimagingservice.medimage import (
    DicomSample,
)


def select_dicom_sample(in_file: DicomDir) -> Path:
    """Select a stable DICOM image from the directory being archived."""
    candidates = sorted(
        path
        for path in in_file.fspath.iterdir()
        if path.is_file()
        and path.name.upper() != "DICOMDIR"
        and DicomImage.matches(path)
    )
    if not candidates:
        raise ValueError(f"No sample DICOM file found in {in_file}")
    return candidates[0]


@converter
@python.define(outputs=["out_file"])  # type: ignore[untyped-decorator]
def SampleDicomDir(
    in_file: DicomDir,
    out_file: ty.Optional[Path] = None,
) -> DicomSample:
    """Copy a representative image directly from a DICOM directory.

    Packaging invokes the generic ZIP and sample converters from the same
    deidentified source, so the sampled bytes also occur in the archive.
    """
    sample = select_dicom_sample(in_file)
    if out_file is None:
        out_file = Path.cwd() / f"{sample.stem}-sample"
    out_file = out_file.absolute()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(sample, out_file)
    return DicomSample(out_file)
