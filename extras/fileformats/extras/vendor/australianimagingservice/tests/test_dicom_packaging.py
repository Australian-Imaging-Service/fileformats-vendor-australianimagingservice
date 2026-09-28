import zipfile
from pathlib import Path

import pytest
from fileformats.application import Zip
from fileformats.medimage import DicomDir, DicomImage
from fileformats.vendor.australianimagingservice import DicomSample

from fileformats.extras.vendor.australianimagingservice.medimage import (
    SampleDicomDir,
    select_dicom_sample,
)


def _dicom(path: Path, payload: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\0" * 128 + b"DICM" + payload)
    return path


def test_directory_uses_generic_zip_and_vendor_sample() -> None:
    assert issubclass(DicomSample, DicomImage)
    zip_converter = Zip[DicomDir].get_converter(DicomDir)
    assert zip_converter is not None
    assert type(zip_converter.task).__name__ == "create_zip"
    sample_converter = DicomSample.get_converter(DicomDir)
    assert sample_converter is not None
    assert isinstance(sample_converter.task, SampleDicomDir)


def test_zip_and_sample_come_from_same_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PYDRA_HASH_CACHE", str(tmp_path / "pydra-hashes"))
    first = _dicom(tmp_path / "source" / "001.dcm", b"first")
    second = _dicom(tmp_path / "source" / "002.dcm", b"second")
    directory = DicomDir(tmp_path / "source")

    archive = Zip[DicomDir].convert(
        directory,
        out_file=tmp_path / "converted.zip",
        compression="ZIP_STORED",
    )
    sample = DicomSample.convert(directory, out_file=tmp_path / "sample")

    assert isinstance(archive, Zip[DicomDir])
    assert select_dicom_sample(directory) == first
    with zipfile.ZipFile(archive) as zf:
        assert zf.read("source/001.dcm") == sample.fspath.read_bytes()
        assert zf.read("source/002.dcm") == second.read_bytes()


def test_sample_selection_excludes_dicomdir(tmp_path: Path) -> None:
    _dicom(tmp_path / "source" / "DICOMDIR", b"directory")
    image = _dicom(tmp_path / "source" / "image.dcm", b"image")

    assert select_dicom_sample(DicomDir(tmp_path / "source")) == image


def test_sample_selection_fails_without_regular_image(tmp_path: Path) -> None:
    _dicom(tmp_path / "source" / "DICOMDIR", b"directory")

    with pytest.raises(ValueError, match="No sample DICOM"):
        select_dicom_sample(DicomDir(tmp_path / "source"))
