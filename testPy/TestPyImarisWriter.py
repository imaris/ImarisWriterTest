#/***************************************************************************
# *   Copyright (c) 2020-present Bitplane AG Zuerich                        *
# *                                                                         *
# *   Licensed under the Apache License, Version 2.0 (the "License");       *
# *   you may not use this file except in compliance with the License.      *
# *   You may obtain a copy of the License at                               *
# *                                                                         *
# *       http://www.apache.org/licenses/LICENSE-2.0                        *
# *                                                                         *
# *   Unless required by applicable law or agreed to in writing, software   *
# *   distributed under the License is distributed on an "AS IS" BASIS,     *
# *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or imp   *
# *   See the License for the specific language governing permissions and   *
# *   limitations under the License.                                        *
# ***************************************************************************/
 
""" Unit Tests for PyImarisWriter classes"""

import unittest
from datetime import datetime

from PyImarisWriter import PyImarisWriter as PW


class TestImageSize(unittest.TestCase):

    def test_incomplete_num_arguments(self):
        with self.assertRaises(PW.PyImarisWriterException):
            image_size = PW.ImageSize(x=2048, y=2048)

    def test_string_instead_of_int(self):
        with self.assertRaises(PW.PyImarisWriterException):
            image_size = PW.ImageSize(x='abc', y=2048, z=100, c=3, t=1)

    def test_wrong_argument_keywords(self):
        with self.assertRaises(PW.PyImarisWriterException):
            image_size = PW.ImageSize(x=2048, y=2048, z=100, c=3, f=1)

    def test_different_arguments_ordering(self):
        val_x = 2048
        val_y = 1024
        image_size = PW.ImageSize(y=val_y, x=val_x, z=100, c=3, t=1)
        self.assertEqual(image_size.x, val_x)
        self.assertEqual(image_size.y, val_y)

    def test_create_block_size(self):
        block_size = PW.ImageSize(x=512, y=512, z=1, c=1, t=1)
        self.assertEqual(block_size.x, 512)
        self.assertEqual(block_size.y, 512)

    def test_image_size_division(self):
        image_size = PW.ImageSize(x=2048, y=2048, z=100, c=3, t=1)
        block_size = PW.ImageSize(x=512, y=512, z=1, c=1, t=1)

        num_blocks = image_size / block_size
        self.assertEqual(num_blocks.x, 4)
        self.assertEqual(num_blocks.y, 4)
        self.assertEqual(num_blocks.z, 100)
        self.assertEqual(num_blocks.c, 3)
        self.assertEqual(num_blocks.t, 1)


class TestDimensionSequence(unittest.TestCase):

    def test_incomplete_num_arguments(self):
        with self.assertRaises(PW.PyImarisWriterException):
            dimension_sequence = PW.DimensionSequence('x')

    def test_duplicate_arguments(self):
        with self.assertRaises(PW.PyImarisWriterException):
            dimension_sequence = PW.DimensionSequence('x', 'y', 'z', 'c', 'x')

    def test_incomplete_num_arguments(self):
        with self.assertRaises(PW.PyImarisWriterException):
            dimension_sequence = PW.DimensionSequence('x', 'y', 'z', 'c', 's')

    def test_uppercase_arguments(self):
        dimension_sequence = PW.DimensionSequence('X', 'y', 'Z', 'c', 'T')
        self.assertEqual(dimension_sequence.get_sequence(), ['x', 'y', 'z', 'c', 't'])

        dimension_sequence = PW.DimensionSequence('T', 'C', 'Z', 'Y', 'X')
        self.assertEqual(dimension_sequence.get_sequence(), ['t', 'c', 'z', 'y', 'x'])


class TestColor(unittest.TestCase):

    def test_default_initializer(self):
        color = PW.Color()

        color = PW.Color(r=0.5, g=0.2, b=0.5, a=1.0)
        self.assertEqual(color.mRed, 0.5)
        self.assertEqual(color.mAlpha, 1.0)

    def test_default_incomplete_initializer(self):
        with self.assertRaises(PW.PyImarisWriterException):
            PW.Color(r=100)


class TestParameters(unittest.TestCase):

    def test_normal_case(self):
        parameters = PW.Parameters()
        section_name = 'Image'
        param_name = 'ImageSizeInMB'
        param_value = 2400
        parameters.set_value(section_name, param_name, param_value)
        self.assertTrue(section_name in parameters.mSections)
        self.assertTrue(param_name in parameters.mSections[section_name])
        self.assertEqual(str(param_value), parameters.mSections[section_name][param_name])
        self.assertEqual(str(param_value), parameters.mSections[section_name][param_name])

    # non string parameters
    def test_c_parameters_creation(self):
        parameters = PW.Parameters()
        parameters.set_value('Image', 'ImageSizeInMB', 2400)
        c_parameters = parameters._get_c_parameters()


class TestOptions(unittest.TestCase):
    def test_set_compression_algorithm(self):
        options = PW.Options()

        # test that default is gzip level 2
        self.assertEqual(options.mCompressionAlgorithmType, PW.eCompressionAlgorithmGzipLevel2)

        # test that setting None stores the value
        options.mCompressionAlgorithmType = PW.eCompressionAlgorithmNone
        self.assertEqual(options.mCompressionAlgorithmType, PW.eCompressionAlgorithmNone)


class TestImageConverter(unittest.TestCase):

    def test_invalid_type(self):
        image_size = None
        sample_size = None
        dimension_sequence = None
        block_size = None
        output_filename = None
        options = None
        application_name = None
        application_version = None
        RecordProgress = None

        with self.assertRaises(PW.PyImarisWriterException):
            converter = PW.ImageConverter('sometype', image_size, sample_size, dimension_sequence, block_size,
                                          output_filename, options, application_name, application_version,
                                          RecordProgress)

        datatype = 'uint8'
        with self.assertRaises(PW.PyImarisWriterException):
            converter = PW.ImageConverter(datatype, image_size, sample_size, dimension_sequence, block_size,
                                          output_filename, options, application_name, application_version,
                                          RecordProgress)

        image_size = PW.ImageSize(x=2048, y=2048, z=100, c=3, t=1)
        with self.assertRaises(PW.PyImarisWriterException):
            converter = PW.ImageConverter(datatype, image_size, sample_size, dimension_sequence, block_size,
                                          output_filename, options, application_name, application_version,
                                          RecordProgress)

        sample_size = PW.ImageSize(x=1, y=1, z=1, c=1, t=1)
        with self.assertRaises(PW.PyImarisWriterException):
            converter = PW.ImageConverter(datatype, image_size, sample_size, dimension_sequence, block_size,
                                          output_filename, options, application_name, application_version,
                                          RecordProgress)

        dimension_sequence = PW.DimensionSequence('x', 'y', 'z', 'c', 't')
        with self.assertRaises(PW.PyImarisWriterException):
            converter = PW.ImageConverter(datatype, image_size, sample_size, dimension_sequence, block_size,
                                          output_filename, options, application_name, application_version,
                                          RecordProgress)

        block_size = PW.ImageSize(x=512, y=512, z=1, c=1, t=1)
        with self.assertRaises(PW.PyImarisWriterException):
            converter = PW.ImageConverter(datatype, image_size, sample_size, dimension_sequence, block_size,
                                          output_filename, options, application_name, application_version,
                                          RecordProgress)

        options = PW.Options()
        with self.assertRaises(PW.PyImarisWriterException):
            converter = PW.ImageConverter(datatype, image_size, sample_size, dimension_sequence, block_size,
                                          output_filename, options, application_name, application_version,
                                          RecordProgress)

        output_filename = 'PyImarisWriterTest.ims'
        application_name = 'UnitTestPyImarisWriter'
        application_version = '0'

        # Progress callback None must fail
        with self.assertRaises(PW.PyImarisWriterException):
            converter = PW.ImageConverter(datatype, image_size, sample_size, dimension_sequence, block_size,
                                          output_filename, options, application_name, application_version,
                                          RecordProgress)

        # Progress callback not having RecordProgress raises exception
        class X():
            pass

        RecordProgress = X()
        with self.assertRaises(PW.PyImarisWriterException):
            converter = PW.ImageConverter(datatype, image_size, sample_size, dimension_sequence, block_size,
                                          output_filename, options, application_name, application_version,
                                          RecordProgress)

        # Progress callback having RecordProgress does not raise exception
        class X2():
            def RecordProgress(self):
                pass

        RecordProgress = X2()
        converter = PW.ImageConverter(datatype, image_size, sample_size, dimension_sequence, block_size,
                                      output_filename, options, application_name, application_version, RecordProgress)

    def test_julian_day(self):
        datetime0 = datetime(1970, 1, 1)
        julianday0 = PW.to_julian_day(datetime0)
        self.assertEqual(julianday0, 2440588)

        datetime_minus = datetime(1969, 12, 30)
        julianday_minus = PW.to_julian_day(datetime_minus)
        self.assertEqual(julianday_minus, 2440586)

        datetime_plus = datetime(1970, 1, 30)
        julianday_plus = PW.to_julian_day(datetime_plus)
        self.assertEqual(julianday_plus, 2440617)

        datetime_2020 = datetime(2020, 2, 5)
        julianday_2020 = PW.to_julian_day(datetime_2020)
        self.assertEqual(julianday_2020, 2458885)

        datetime_2021 = datetime(2021, 6, 1)
        julianday_2021 = PW.to_julian_day(datetime_2021)
        self.assertEqual(julianday_2021, 2459367)

    def test_time_infos(self):
        time_info = datetime.strptime('2020-02-05 15:27.04', '%Y-%m-%d %H:%M.%S')

        c_time_info = PW.get_c_time_info(time_info)

        julian_day = 2458885  # 5 feb 2020
        seconds = 4 + 60 * (27 + 60 * 15)  # 3:27.04 PM
        nanoseconds = seconds * 1e9
        self.assertEqual(c_time_info.mJulianDay, int(julian_day))
        self.assertEqual(c_time_info.mNanosecondsOfDay, int(nanoseconds))


if __name__ == "__main__":
    unittest.main()