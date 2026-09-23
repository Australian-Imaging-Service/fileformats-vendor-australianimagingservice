from fileformats.application import Dicom
from fileformats.image import Gif
from fileformats.medimage.base import MedicalImage


class XnatSnapshot(MedicalImage, Gif):
    """A PNG snapshot of a image to be displayed in XNAT's UI"""


class DicomSample(MedicalImage, Dicom):
    """An extracted DICOM slice to be stored alongside a DICOM zip
    archive so its metadata can be extracted"""

    ext = None
