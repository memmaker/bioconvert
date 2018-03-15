import os

import pytest
from easydev import TempFile, md5

from bioconvert import bioconvert_data
from bioconvert.csv2tsv import CSV2TSV


@pytest.mark.parametrize("method", CSV2TSV.available_methods)
def test_conv(method):
    infile = bioconvert_data("test_v1.csv")
    expected_outile = bioconvert_data("test_v1.tsv")
    with TempFile(suffix=".tsv") as tempfile:
        convert = CSV2TSV(infile, tempfile.name)
        convert()
        assert md5(tempfile.name) == md5(expected_outile)
