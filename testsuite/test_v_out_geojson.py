#
########################################################################################
# MODULE:     v.out.geojson test
# AUTHOR(S):  Anika Weinmann
# PURPOSE:    Tests v.out.geojson inputs.
#             Uses NC full sample data set.
# COPYRIGHT:  (C) 2020-2022 mundialis GmbH & Co. KG and the GRASS Development Team
# LICENSE:    This program is free software; you can redistribute it and/or modify
#             it under the terms of the GNU General Public License as published by
#             the Free Software Foundation; either version 2 of the License, or
#             (at your option) any later version.
#
#             This program is distributed in the hope that it will be useful,
#             but WITHOUT ANY WARRANTY; without even the implied warranty of
#             MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#             GNU General Public License for more details.
#
########################################################################################

import os

from grass.gunittest.case import TestCase
from grass.gunittest.main import test
from grass.gunittest.gmodules import SimpleModule


class TestVOutGeojson(TestCase):
    area_file = "data/area.geojson"
    geojson_epsg4326 = "data/area_epsg4326.geojson"
    geojson_epsg3358 = "data/area_epsg3358.geojson"
    geojson_stdout = (
        '{"crs": {"properties": '
        '{"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}, "type": "name"}, '
        '"features": [{"geometry": {"coordinates": '
        "[[[-78.802185, 35.894613], [-78.809052, 35.894057], "
        "[-78.817978, 35.890163], [-78.839951, 35.861787], "
        "[-78.879776, 35.845091], [-78.894196, 35.825608], "
        "[-78.881149, 35.7805], [-78.894196, 35.754314], "
        "[-78.876343, 35.696341], [-78.835831, 35.686302], "
        "[-78.748398, 35.684629], [-78.660965, 35.682956], "
        "[-78.573532, 35.681283], [-78.540916, 35.717798], "
        "[-78.508301, 35.754314], [-78.515854, 35.825608], "
        "[-78.558426, 35.870134], [-78.62915, 35.903512], "
        "[-78.698502, 35.915747], [-78.802185, 35.894613]]], "
        '"type": "Polygon"}, "properties": '
        '{"cat": 1}, "type": "Feature"}], "name": "tmp_test_area", '
        '"type": "FeatureCollection"}\n'
    )
    pid_str = str(os.getpid())
    area = "tmp_test_area"
    region = "region_%s" % pid_str
    geojson_file = "geoson_%s.geojson" % pid_str

    @classmethod
    def setUpClass(self):
        """Ensures expected computational region and generated data"""
        # import general area
        self.runModule("v.import", input=self.area_file, output=self.area)
        # set temp region
        self.runModule("g.region", save=self.region)
        # set region to area
        self.runModule("g.region", vector=self.area)

    @classmethod
    def tearDownClass(self):
        """Remove the temporary region and generated data"""
        self.runModule("g.remove", type="vector", name=self.area, flags="f")
        self.runModule("g.region", region=self.region)
        self.runModule("g.remove", type="region", name=self.region, flags="f")

    def tearDown(self):
        """Remove the outputs created
        This is executed after each test run.
        """
        if os.path.isfile(self.geojson_file):
            os.remove(self.geojson_file)

    def test_export_to_geojson(self):
        """Test export to geojson file"""
        v_out_geojson = SimpleModule(
            "v.out.geojson", input=self.area, output=self.geojson_file
        )
        self.assertModule(v_out_geojson)
        # test that error output is not empty
        stderr = v_out_geojson.outputs.stderr
        self.assertTrue(stderr)
        # test that the right map is mentioned in the error message
        self.assertIn(
            "GeoJSON of <%s> in EPSG:<4326> is saved in <%s>"
            % (self.area, self.geojson_file),
            stderr,
        )
        # check to see if output file exists
        self.assertFileExists(self.geojson_file, msg="Output file does not exist")
        # check if the output file is equal to the reference file
        self.assertFilesEqualMd5(
            self.geojson_file,
            self.geojson_epsg4326,
            msg="Output file is not equal to reference file",
        )

    def test_export_to_geojson_epsg4326(self):
        """Test export to geojson file with epsg:4326"""
        epsg = 4326
        geojson = self.geojson_epsg4326
        v_out_geojson = SimpleModule(
            "v.out.geojson", input=self.area, output=self.geojson_file, epsg=epsg
        )
        self.assertModule(v_out_geojson)
        # test that error output is not empty
        stderr = v_out_geojson.outputs.stderr
        self.assertTrue(stderr)
        # test that the right map is mentioned in the error message
        self.assertIn(
            "GeoJSON of <%s> in EPSG:<%d> is saved in <%s>"
            % (self.area, epsg, self.geojson_file),
            stderr,
        )
        # check to see if output file exists
        self.assertFileExists(self.geojson_file, msg="Output file does not exist")
        # check if the output file is equal to the reference file
        self.assertFilesEqualMd5(
            self.geojson_file, geojson, msg="Output file is not equal to reference file"
        )

    def test_export_to_geojson_epsg3358(self):
        """Test export to geojson file with epsg:3358"""
        epsg = 3358
        geojson = self.geojson_epsg3358
        v_out_geojson = SimpleModule(
            "v.out.geojson", input=self.area, output=self.geojson_file, epsg=epsg
        )
        self.assertModule(v_out_geojson)
        # test that error output is not empty
        stderr = v_out_geojson.outputs.stderr
        self.assertTrue(stderr)
        # test that the right map is mentioned in the error message
        self.assertIn(
            "GeoJSON of <%s> in EPSG:<%d> is saved in <%s>"
            % (self.area, epsg, self.geojson_file),
            stderr,
        )
        # check to see if output file exists
        self.assertFileExists(self.geojson_file, msg="Output file does not exist")
        # check if the output file is equal to the reference file
        self.assertFilesEqualMd5(
            self.geojson_file, geojson, msg="Output file is not equal to reference file"
        )

    def test_export_to_geojson_stdout(self):
        """Test export in geojson format to stdout"""
        epsg = 4326
        v_out_geojson = SimpleModule("v.out.geojson", input=self.area, output="-")
        self.assertModule(v_out_geojson)
        # test that error output is not empty
        stderr = v_out_geojson.outputs.stderr
        self.assertTrue(stderr)
        # test that the right map is mentioned in the error message
        self.assertIn("GeoJSON of <%s> in EPSG:<%d> is:" % (self.area, epsg), stderr)
        # check geojson in stdout
        stdout = v_out_geojson.outputs.stdout
        self.assertEqual(self.geojson_stdout, stdout)

    def test_export_to_geojson_stdout_epsgerror(self):
        """Test export in geojson format to stdout"""
        epsg = 335888
        v_out_geojson = SimpleModule(
            "v.out.geojson", input=self.area, output="-", epsg=epsg
        )
        self.assertModuleFail(v_out_geojson)
        # test that error output is not empty
        stderr = v_out_geojson.outputs.stderr
        self.assertTrue(stderr)
        # test that the right map is mentioned in the error message
        self.assertIn(
            "EPSG PCS/GCS code %d not found in EPSG support files.  "
            "Is this a valid EPSG coordinate system?\n" % (epsg),
            stderr,
        )


if __name__ == "__main__":
    test()
