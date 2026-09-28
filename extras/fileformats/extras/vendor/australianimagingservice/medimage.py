# Implement 'extras' for the formats defined in
# fileformats.vendor.australianimagingservice.medimage here, see
# https://arcanaframework.github.io/fileformats/developer/extras.html

import shutil
import typing as ty
import zipfile
from pathlib import Path

from fileformats.application import Zip
from fileformats.core import converter
from fileformats.medimage import DicomSeries
from pydra.compose import python

from fileformats.vendor.australianimagingservice.medimage import (
    DicomSample,
)

ZIPPED_DICOM_SERIES: type[Zip] = Zip[DicomSeries]  # type: ignore[misc]


def select_dicom_sample(in_file: DicomSeries) -> Path:
    """Select a stable sample from a DICOM series.

    The same sorted relative paths are used by the zip converter below, so the
    selected file is guaranteed to be an unmodified member of its archive output.
    """
    candidates = sorted(
        (Path(path) for path in in_file.fspaths),
        key=lambda path: str(path.relative_to(in_file.parent)),
    )
    candidates = [
        path
        for path in candidates
        if path.is_file() and path.name.upper() != "DICOMDIR"
    ]
    if not candidates:
        raise ValueError(f"No sample DICOM file found in {in_file}")
    return candidates[0]


def zip_dicom_series(
    in_file: DicomSeries,
    out_file: Path,
    compression: int = zipfile.ZIP_STORED,
    allowZip64: bool = True,
    compresslevel: int | None = None,
    strict_timestamps: bool = True,
) -> Zip:
    """Archive a DICOM series without modifying its members."""
    if isinstance(compression, str):
        try:
            compression = getattr(zipfile, compression)
        except AttributeError as e:
            raise ValueError(f"Unknown ZIP compression method {compression!r}") from e

    out_file = out_file.absolute()
    with zipfile.ZipFile(
        out_file,
        mode="w",
        compression=compression,
        allowZip64=allowZip64,
        compresslevel=compresslevel,
        strict_timestamps=strict_timestamps,
    ) as archive:
        for path in sorted(
            (Path(path) for path in in_file.fspaths),
            key=lambda path: str(path.relative_to(in_file.parent)),
        ):
            archive.write(path, arcname=path.relative_to(in_file.parent))
    return ZIPPED_DICOM_SERIES(out_file)


@converter
@python.define(outputs=["out_file"])  # type: ignore[untyped-decorator]
def ZipDicomSeries(
    in_file: DicomSeries,
    out_file: ty.Optional[Path] = None,
    compression: int = zipfile.ZIP_STORED,
    allowZip64: bool = True,
    compresslevel: ty.Optional[int] = None,
    strict_timestamps: bool = True,
) -> Zip:
    """Create a typed zip containing every member of a DICOM series."""
    if out_file is None:
        out_file = Path.cwd() / "dicom-series.zip"
    return zip_dicom_series(
        in_file,
        out_file,
        compression=compression,
        allowZip64=allowZip64,
        compresslevel=compresslevel,
        strict_timestamps=strict_timestamps,
    )


@converter
@python.define(outputs=["out_file"])  # type: ignore[untyped-decorator]
def SampleDicomSeries(
    in_file: DicomSeries,
    out_file: ty.Optional[Path] = None,
) -> DicomSample:
    """Copy a representative file directly from a DICOM series.

    This is deliberately does not go through ``Zip[DicomSeries]``: packaging invokes
    both converters from the same already-deidentified source, avoiding a redundant
    archive read while guaranteeing the copied bytes also occur in the zip.
    """
    sample = select_dicom_sample(in_file)
    if out_file is None:
        out_file = Path.cwd() / f"{sample.stem}-sample"
    out_file = out_file.absolute()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(sample, out_file)
    return DicomSample(out_file)
