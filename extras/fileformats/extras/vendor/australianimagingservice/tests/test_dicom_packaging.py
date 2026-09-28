import zipfile
from pathlib import Path

import pytest
from fileformats.application import Zip
from fileformats.medimage import DicomImage, DicomSeries
from fileformats.vendor.australianimagingservice import DicomSample

from fileformats.extras.vendor.australianimagingservice.medimage import (
    select_dicom_sample,
    zip_dicom_series,
)


def _dicom(path: Path, payload: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\0" * 128 + b"DICM" + payload)
    return path


def test_dicom_series_converters_are_registered() -> None:
    assert issubclass(DicomSample, DicomImage)
    assert Zip[DicomSeries].get_converter(DicomSeries) is not None
    assert DicomSample.get_converter(DicomSeries) is not None


def test_zip_and_sample_are_derived_from_the_same_series(tmp_path: Path) -> None:
    first = _dicom(tmp_path / "source" / "a" / "001.dcm", b"first")
    second = _dicom(tmp_path / "source" / "b" / "002.dcm", b"second")
    series = DicomSeries([second, first])

    sample = select_dicom_sample(series)
    archive = zip_dicom_series(series, tmp_path / "series.zip")

    assert sample == first
    with zipfile.ZipFile(archive) as zf:
        assert zf.namelist() == ["a/001.dcm", "b/002.dcm"]
        assert zf.read("a/001.dcm") == sample.read_bytes()
        assert zf.read("b/002.dcm") == second.read_bytes()


def test_sample_selection_excludes_dicomdir(tmp_path: Path) -> None:
    dicomdir = _dicom(tmp_path / "source" / "DICOMDIR", b"directory")
    image = _dicom(tmp_path / "source" / "image.dcm", b"image")

    assert select_dicom_sample(DicomSeries([dicomdir, image])) == image


def test_sample_selection_fails_without_regular_image(tmp_path: Path) -> None:
    dicomdir = _dicom(tmp_path / "source" / "DICOMDIR", b"directory")

    with pytest.raises(ValueError, match="No sample DICOM"):
        select_dicom_sample(DicomSeries([dicomdir]))
