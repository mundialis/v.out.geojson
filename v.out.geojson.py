#!/usr/bin/env python3
#
########################################################################################
#
# MODULE:      v.out.geojson
# AUTHOR(S):   Anika Weinmann
# PURPOSE:     Exports vector map to GeoJSON format into projection with given EPSG code
# COPYRIGHT:   (C) 2020-2022 by mundialis GmbH & Co. KG and the GRASS Development Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
########################################################################################

# %module
# % description: Exports vector map to GeoJSON format into projection with given EPSG code.
# % keyword: vector
# % keyword: export
# % keyword: projection
# %end

# %option G_OPT_V_INPUT
# % key: input
# % required: yes
# % description: Input vector map
# %end

# %option G_OPT_F_OUTPUT
# % key: output
# % required: yes
# % description: Output GeoJSON file. "-" to write to stdout
# %end

# %option
# % key: epsg
# % type: integer
# % required: no
# % multiple: no
# % description: Output EPSG code
# % guisection: Filter
# % answer: 4326
# % end


import atexit
import geojson
import os
import sys

import grass.script as grass

# initialize global vars
rm_file = []
TMPLOC = None
SRCGISRC = None
TGTGISRC = None
GISDBASE = None


def cleanup():
    grass.message(_("Cleaning up..."))
    # nuldev = open(os.devnull, 'w')
    for rm_f in rm_file:
        if os.path.isfile(rm_f):
            os.remove(rm_f)
    if TGTGISRC:
        os.environ["GISRC"] = str(TGTGISRC)
    # remove temp location
    if TMPLOC:
        grass.try_rmdir(os.path.join(GISDBASE, TMPLOC))
    if SRCGISRC:
        grass.try_remove(SRCGISRC)


def createTMPlocation(epsg=4326):
    global TMPLOC, SRCGISRC
    SRCGISRC = grass.tempfile()
    TMPLOC = "temp_import_location_" + str(os.getpid())
    f = open(SRCGISRC, "w")
    f.write("MAPSET: PERMANENT\n")
    f.write("GISDBASE: %s\n" % GISDBASE)
    f.write("LOCATION_NAME: %s\n" % TMPLOC)
    f.write("GUI: text\n")
    f.close()

    proj_test = grass.parse_command("g.proj", flags="g")
    if "epsg" in proj_test:
        epsg_arg = {"epsg": epsg}
    else:
        epsg_arg = {"srid": "EPSG:{}".format(epsg)}
    # create temp location from input without import
    grass.verbose(_("Creating temporary location with EPSG:%d...") % epsg)
    grass.run_command("g.proj", flags="c", location=TMPLOC, quiet=True, **epsg_arg)

    # switch to temp location
    os.environ["GISRC"] = str(SRCGISRC)
    proj = grass.parse_command("g.proj", flags="g")
    if "epsg" in proj:
        new_epsg = proj["epsg"]
    else:
        new_epsg = proj["srid"].split("EPSG:")[1]
    if new_epsg != str(epsg):
        grass.fatal(_("Creation of temporary location failed!"))


def get_actual_location():
    global TGTGISRC, GISDBASE
    # get actual location, mapset, ...
    grassenv = grass.gisenv()
    tgtloc = grassenv["LOCATION_NAME"]
    tgtmapset = grassenv["MAPSET"]
    GISDBASE = grassenv["GISDBASE"]
    TGTGISRC = os.environ["GISRC"]
    return tgtloc, tgtmapset


def main():

    global rm_file
    global TMPLOC, SRCGISRC, TGTGISRC, GISDBASE

    vect = options["input"]

    # set some common environmental variables, like:
    os.environ.update(
        dict(
            GRASS_COMPRESS_NULLS="1",
            GRASS_COMPRESSOR="LZ4",
            GRASS_MESSAGE_FORMAT="plain",
        )
    )

    # input vector map to GeoJSON
    grass.message(_("Export input as GeoJSON..."))
    # get actual location, mapset, ...
    tgtloc, tgtmapset = get_actual_location()
    # create temporary location with epsg:4326
    createTMPlocation(int(options["epsg"]))

    if "@" in vect:
        [name, vectmapset] = vect.split("@")
    else:
        name, vectmapset = vect, tgtmapset

    # reproject vector
    grass.run_command(
        "v.proj",
        location=tgtloc,
        mapset=vectmapset,
        input=name,
        output=name,
        quiet=True,
    )

    if options["output"] == "-":
        geojsonfile = "%s.geojson" % grass.tempname(8)
        rm_file.append(geojsonfile)
    else:
        geojsonfile = options["output"]
    grass.run_command("v.out.ogr", input=name, output=geojsonfile, format="GeoJSON")
    if options["output"] == "-":
        with open(geojsonfile) as f:
            gj = geojson.load(f)
        grass.message(
            _("GeoJSON of <%s> in EPSG:<%s> is:") % (options["input"], options["epsg"])
        )
        print(gj)
    else:
        grass.message(
            _("GeoJSON of <%s> in EPSG:<%s> is saved in <%s>")
            % (options["input"], options["epsg"], options["output"])
        )
    # switch to target location
    os.environ["GISRC"] = str(TGTGISRC)

    return 0


if __name__ == "__main__":
    options, flags = grass.parser()
    atexit.register(cleanup)
    sys.exit(main())
