# Implement 'extras' for the formats defined in
# fileformats.vendor.australianimagingservice.medimage here, see
# https://arcanaframework.github.io/fileformats/developer/extras.html

from fileformats.core import converter
from fileformats.application import Zip
from fileformats.medimage import DicomSeries
from pydra.compose import python

from fileformats.vendor.australianimagingservice.medimage import (
    DicomSample,
    XnatSnapshot,
)


@converter
@python.define(outputs=["out_file"])  # type: ignore[untyped-decorator]
def SnapshotZippedDicomCollection(
    in_file: Zip[DicomSeries],  # type: ignore[type-arg]
) -> XnatSnapshot:
    """Snapshots of a DICOM collection for display in XNAT's UI

    Parameters
    ----------
    in_file : Zip[DicomSeries]
        the input zipped DICOM series to create snapshots from

    Returns
    -------
    out_file: XnatSnapshot
        the resulting XNAT snapshot of the DICOM collection

    Raises
    ------
    ValueError
        when mutually exclusive "extract_volume" and "to_4d" options are provided
    """
    raise NotImplementedError(
        "SnapshotDicomCollection converter is not yet implemented"
    )


@converter
@python.define(outputs=["out_file"])  # type: ignore[untyped-decorator]
def SampleZippedDicomCollection(
    in_file: Zip[DicomSeries],  # type: ignore[type-arg]
) -> DicomSample:
    """Samples a DICOM collection from a zipped DICOM collection

    Parameters
    ----------
    in_file : Zip[DicomSeries]
        the input zipped DICOM series to create a sample from

    Returns
    -------
    out_file: DicomSample
        the resulting sample of the DICOM collection

    Raises
    ------
    ValueError
        when mutually exclusive "extract_volume" and "to_4d" options are provided
    """
    raise NotImplementedError("SampleDicomCollection converter is not yet implemented")
