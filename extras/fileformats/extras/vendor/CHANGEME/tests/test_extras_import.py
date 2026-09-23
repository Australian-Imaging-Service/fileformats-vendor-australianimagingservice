def test_extras_pkg_import():

    import fileformats.extras.vendor.CHANGEME

    assert (
        fileformats.extras.vendor.CHANGEME.__name__
        == "fileformats.extras.vendor.CHANGEME"
    )
