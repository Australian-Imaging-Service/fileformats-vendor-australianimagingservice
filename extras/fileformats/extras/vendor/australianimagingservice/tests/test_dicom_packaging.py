from fileformats.application import Zip
from fileformats.medimage import DicomDir, DicomImage
from fileformats.vendor.australianimagingservice import DicomSample

from fileformats.extras.vendor.australianimagingservice.medimage import (
    SampleDicomDir,
)


def test_directory_uses_generic_zip_and_vendor_sample() -> None:
    assert issubclass(DicomSample, DicomImage)
    zip_converter = Zip[DicomDir].get_converter(DicomDir)
    assert zip_converter is not None
    assert type(zip_converter.task).__name__ == "create_zip"
    sample_converter = DicomSample.get_converter(DicomDir)
    assert sample_converter is not None
    assert isinstance(sample_converter.task, SampleDicomDir)
