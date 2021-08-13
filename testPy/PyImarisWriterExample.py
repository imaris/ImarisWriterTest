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
Example Program that creates an ims file using PyImarisWriter python library, similar to bpImarisWriter96TestProgram.c
"""

from PyImarisWriter import PyImarisWriter as PW

from datetime import datetime


class MyCallbackClass(PW.CallbackClass):
    def __init__(self):
        self.mUserDataProgress = 0

    def RecordProgress(self, progress, total_bytes_written):
        progress100 = int(progress * 100)
        if progress100 - self.mUserDataProgress >= 5:
            self.mUserDataProgress = progress100
            print('User Progress {}, Bytes written: {}'.format(self.mUserDataProgress, total_bytes_written))


def main():
    image_size = PW.ImageSize(x=512, y=512, z=32, c=3, t=4)
    dimension_sequence = PW.DimensionSequence('x', 'y', 'z', 'c', 't')
    block_size = PW.ImageSize(x=512, y=512, z=1, c=1, t=1)
    sample_size = PW.ImageSize(x=1, y=1, z=1, c=1, t=1)
    num_voxels_per_block = block_size.x * block_size.y * block_size.z * block_size.c * block_size.t
    output_filename = 'PyImarisWriterTest.ims'
    
    options = PW.Options()
    options.mNumberOfThreads = 12
    options.mCompressionAlgorithmType = PW.eCompressionAlgorithmGzipLevel2
    options.mEnableLogProgress = True

    voxel_data = (PW.c_uint16 * num_voxels_per_block)()
    for i in range(num_voxels_per_block):
        voxel_data[i] = i % 256
        
    application_name = 'PyImarisWriter'
    application_version = '1.0.0'

    callback_class = MyCallbackClass()
    converter = PW.ImageConverter('uint16', image_size, sample_size, dimension_sequence, block_size,
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
                            converter.CopyBlock(voxel_data, block_index)

    adjust_color_range = True
    image_extents = PW.ImageExtents(0, 0, 0, 10, 10, 10)
    parameters = PW.Parameters()
    parameters.set_value('Image', 'ImageSizeInMB', 2400)
    parameters.set_channel_name(0, 'My Channel 1')
    time_infos = [datetime.today()]
    color_infos = [PW.ColorInfo() for _ in range(image_size.c)]
    color_infos[1].set_base_color(PW.Color(0, 1, 0, 1))
    color_infos[2].set_color_table([PW.Color(0, 1, 1, 1), PW.Color(1, 0, 1, 1), PW.Color(1, 1, 0, 1),
                                    PW.Color(1, 1, 1, 1), PW.Color(0, 0, 0, 1), PW.Color(1, 0, 0, 1)])

    converter.Finish(image_extents, parameters, time_infos, color_infos, adjust_color_range)
    
    converter.Destroy()
    print('Wrote {}'.format(output_filename))


if __name__ == "__main__":
    main()
