# -*- coding: utf-8 -*-
#
#  This file is part of Bioconvert software
#
#  Copyright (c) 2017 - Bioconvert Development Team
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/biokit/bioconvert
#  documentation: http://bioconvert.readthedocs.io
#
##############################################################################
"""Provides a general tool to perform pre/post compression"""
from functools import wraps
from os.path import splitext
from bioconvert import logger

def in_gz(func):
    """Marks a function as accepting gzipped input."""
    func.in_gz = True
    return func

def compressor(func):
    """Decompress/compress input file without pipes

    Does not use pipe: we decompress and compress back the input file.
    The advantage is that it should work for any files (even very large).

    This decorator should be used by method that uses pure python code
    """
    # https://stackoverflow.com/a/309000/1878788
    @wraps(func)
    def wrapped(inst, *args, **kwargs):
        infile_name = inst.infile

        output_compressed = None
        if inst.outfile.endswith(".gz"):
            (inst.outfile, output_compressed) = splitext(inst.outfile)
        elif inst.outfile.endswith(".bz2"):
            (inst.outfile, output_compressed) = splitext(inst.outfile)
        elif inst.outfile.endswith(".dsrc"):  # !!! only for fastq files
            (inst.outfile, output_compressed) = splitext(inst.outfile)
        # Now inst has the uncompressed output file name

        if infile_name.endswith(".gz"):
            # decompress input
            # TODO: https://stackoverflow.com/a/29371584/1878788
            logger.info("Generating uncompressed version of %s " % infile_name)
            (inst.infile, _) = splitext(inst.infile)
            inst.shell("unpigz -c -p {} {} > {}".format(
                inst.threads, infile_name, inst.infile))
            # computation
            results = func(inst, *args, **kwargs)
            inst.infile = infile_name
        else:
            results = func(inst, *args, **kwargs)

        # Compress output and restore inst output file name
        if output_compressed == ".gz":
            # TODO: this uses -f ; should be a
            logger.info("Compressing output into .gz")
            inst.shell("pigz -f -p {} {}".format(inst.threads, inst.outfile))
            inst.outfile = inst.outfile + ".gz"
        elif output_compressed == ".bz2":
            logger.info("Compressing output into .bz2")
            inst.shell("pbzip2 -f -p{} {}".format(inst.threads, inst.outfile))
            inst.outfile = inst.outfile + ".bz2"
        elif output_compressed == ".dsrc":  # !!! only for FastQ files
            logger.info("Compressing output into .dsrc")
            inst.shell("dsrc c -t{} {} {}.dsrc".format(
                inst.threads, inst.outfile, inst.outfile))
            inst.outfile = inst.outfile + ".dsrc"
        return results
    return in_gz(wrapped)

def out_compressor(func):
    """Compress output file without pipes

    This decorator should be used by method that uses pure python code
    """
    # https://stackoverflow.com/a/309000/1878788
    @wraps(func)
    def wrapped(inst, *args, **kwargs):
        output_compressed = None
        if inst.outfile.endswith(".gz"):
            (inst.outfile, output_compressed) = splitext(inst.outfile)
        elif inst.outfile.endswith(".bz2"):
            (inst.outfile, output_compressed) = splitext(inst.outfile)
        elif inst.outfile.endswith(".dsrc"):  # !!! only for fastq files
            (inst.outfile, output_compressed) = splitext(inst.outfile)
        # Now inst has the uncompressed output file name

        # computation
        results = func(inst, *args, **kwargs)

        # Compress output and restore inst output file name
        if output_compressed == ".gz":
            # TODO: this uses -f ; should be a
            logger.info("Compressing output into .gz")
            inst.shell("pigz -f -p {} {}".format(inst.threads, inst.outfile))
            inst.outfile = inst.outfile + ".gz"
        elif output_compressed == ".bz2":
            logger.info("Compressing output into .bz2")
            inst.shell("pbzip2 -f -p{} {}".format(inst.threads, inst.outfile))
            inst.outfile = inst.outfile + ".bz2"
        elif output_compressed == ".dsrc":  # !!! only for FastQ files
            logger.info("Compressing output into .dsrc")
            inst.shell("dsrc c -t{} {} {}.dsrc".format(
                inst.threads, inst.outfile, inst.outfile))
            inst.outfile = inst.outfile + ".dsrc"
        return results
    return wrapped
