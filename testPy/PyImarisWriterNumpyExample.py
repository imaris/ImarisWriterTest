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

"""
Example Program that creates an ims file from numpy array using PyImarisWriter python library
"""

from PyImarisWriter import PyImarisWriter as PW
import numpy as np

from datetime import datetime

class TestConfiguration:

    def __init__(self, id, title, np_type, imaris_type, color_table):
        self.mId = id
        self.mTitle = title
        self.mNp_type = np_type
        self.mImaris_type = imaris_type
        self.mColor_table = color_table

def get_test_configurations():
    configurations = []

    configurations.append(TestConfiguration(len(configurations), 'uint8 image from uint8 numpy array', np.uint8, 'uint8',
                                            [PW.Color(0.086, 0.608, 0.384, 1), PW.Color(1, 1, 1, 1), PW.Color(1, 0.533, 0.243, 1)]))

    configurations.append(TestConfiguration(len(configurations), 'uint16 image from uint16 numpy array', np.uint16, 'uint16',
                                            [PW.Color(0, 0.169, 0.498, 1), PW.Color(0.988, 0.820, 0.086, 1), PW.Color(1, 0, 0, 1)]))

    configurations.append(TestConfiguration(len(configurations), 'float32 image from float32 numpy array', np.float32, 'float32',
                                            [PW.Color(0, 0, 0, 1), PW.Color(0.992, 0.855, 0.141, 1), PW.Color(0.937, 0.200, 0.251, 1)]))

    configurations.append(TestConfiguration(len(configurations), 'uint16 image from uint8 numpy array', np.uint8, 'uint16',
                                            [PW.Color(0, 0, 1, 1), PW.Color(1, 1, 1, 1), PW.Color(1, 0, 0, 1)]))

    configurations.append(TestConfiguration(len(configurations), 'float32 image from uint8 numpy array', np.uint8, 'float32',
                                            [PW.Color(0, 1, 0, 1), PW.Color(1, 1, 1, 1), PW.Color(1, 0, 0, 1)]))

    configurations.append(TestConfiguration(len(configurations), 'float32 image from uint16 numpy array', np.uint16, 'float32',
                                            [PW.Color(0, 1, 1, 1), PW.Color(1, 0, 1, 1), PW.Color(1, 1, 0, 1)]))

    return configurations



class MyCallbackClass(PW.CallbackClass):
    def __init__(self):
        self.mUserDataProgress = 0

    def RecordProgress(self, progress, total_bytes_written):
        progress100 = int(progress * 100)
        if progress100 - self.mUserDataProgress >= 5:
            self.mUserDataProgress = progress100
            print('User Progress {}, Bytes written: {}'.format(self.mUserDataProgress, total_bytes_written))


def run(configuration):
    image_size = PW.ImageSize(x=600, y=400, z=5, c=1, t=1)
    dimension_sequence = PW.DimensionSequence('x', 'y', 'z', 'c', 't')
    block_size = image_size
    sample_size = PW.ImageSize(x=1, y=1, z=1, c=1, t=1)
    output_filename = f'PyImarisWriterNumpyExample{configuration.mId}.ims'
    
    options = PW.Options()
    options.mNumberOfThreads = 12
    options.mCompressionAlgorithmType = PW.eCompressionAlgorithmGzipLevel2
    options.mEnableLogProgress = True

    np_data = np.zeros((image_size.z, image_size.y, image_size.x), dtype=configuration.mNp_type)
    x1 = int(image_size.x / 3)
    x2 = int(image_size.x / 3 * 2)
    np_data[:,:,0:x1] = 10.0
    np_data[:,:,x1:x2] = 130.0
    np_data[:,:,x2:] = 240.0

    application_name = 'PyImarisWriter'
    application_version = '1.0.0'

    callback_class = MyCallbackClass()
    converter = PW.ImageConverter(configuration.mImaris_type, image_size, sample_size, dimension_sequence, block_size,
                                  output_filename, options, application_name, application_version, callback_class)
    
    num_blocks = image_size / block_size

    block_index = PW.ImageSize()
    for c in range(num_blocks.c):
        block_index.c = c
        for t in range(num_blocks.t):
            block_index.t = t
            for z in range(num_blocks.z):
                block_index.z = z
                for y in range(num_blocks.y):
                    block_index.y = y
                    for x in range(num_blocks.x):
                        block_index.x = x
                        if converter.NeedCopyBlock(block_index):
                            converter.CopyBlock(np_data, block_index)

    adjust_color_range = True
    image_extents = PW.ImageExtents(0, 0, 0, image_size.x, image_size.y, image_size.z)
    parameters = PW.Parameters()
    parameters.set_value('Image', 'ImageSizeInMB', 2400)
    parameters.set_value('Image', 'Info', configuration.mTitle)
    parameters.set_channel_name(0, 'My Channel 1')
    time_infos = [datetime.today()]
    color_infos = [PW.ColorInfo() for _ in range(image_size.c)]
    color_infos[0].set_color_table(configuration.mColor_table)

    converter.Finish(image_extents, parameters, time_infos, color_infos, adjust_color_range)
    
    converter.Destroy()
    print('Wrote {} to {}'.format(configuration.mTitle, output_filename))


def main():
    configurations = get_test_configurations()
    for test_config in configurations:
            run(test_config)

if __name__ == "__main__":
    main()
