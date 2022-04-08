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
Python Version of bpImarisWriter96TestProgram.c that uses ImarisWriterCtypes
"""

import platform
import sys

from PyImarisWriter import ImarisWriterCtypes as IW

def check_errors(cdll, imageconverter_ptr):
    cdll.bpImageConverterC_GetLastException.restype = IW.c_char_p
    last_exception = cdll.bpImageConverterC_GetLastException(imageconverter_ptr)
    if last_exception:
        print('Error occured, exiting application.\nError: "{}"'.format(last_exception.decode()))
        sys.exit(1)

          
# class PySize5D

def get_image_size():
    return IW.bpConverterTypesC_Size5DPtr(IW.bpConverterTypesC_Size5D(512, 512, 32, 2, 4))
    
def get_image_extents(image_size):
    voxel_size_xy = 1.4
    voxel_size_z = 5.4
    return IW.bpConverterTypesC_ImageExtentPtr(IW.bpConverterTypesC_ImageExtent(0, 0, 0, \
        image_size.mValueX * voxel_size_xy,
        image_size.mValueY * voxel_size_xy,
        image_size.mValueZ * voxel_size_z)) 

def get_sample():
    return IW.bpConverterTypesC_Size5DPtr(IW.bpConverterTypesC_Size5D(1, 1, 1, 1, 1))
    
def get_dimension_sequence():
    return IW.bpConverterTypesC_DimensionSequence5DPtr(IW.bpConverterTypesC_DimensionSequence5D(IW.bpConverterTypesC_DimensionX,
                                                    IW.bpConverterTypesC_DimensionY,
                                                    IW.bpConverterTypesC_DimensionZ,
                                                    IW.bpConverterTypesC_DimensionC,
                                                    IW.bpConverterTypesC_DimensionT))
                                                    
def get_block_size():
    return IW.bpConverterTypesC_Size5DPtr(IW.bpConverterTypesC_Size5D(256, 256, 8, 1, 1))
    
def get_options():
    enable_log_progress = False
    num_threads = 8
    
    return IW.bpConverterTypesC_OptionsPtr(IW.bpConverterTypesC_Options(256, False, False, False, False, enable_log_progress, num_threads, IW.eCompressionAlgorithmGzipLevel2))

def num_blocks_1D(size, block_size):
    return int((size + block_size - 1) / block_size)
    
import random
def copy_blocks(cdll, imageconverter_ptr, image_size, block_size):
    num_voxels_per_block = block_size.mValueX * block_size.mValueY * block_size.mValueZ * block_size.mValueC * block_size.mValueT
    voxel_data = (IW.c_ubyte * num_voxels_per_block)()
    for i in range(num_voxels_per_block):
        voxel_data[i] = i % 256
        #voxel_data[i] = int(random.random() * 256)
    
    num_blocks_x = num_blocks_1D(image_size.mValueX, block_size.mValueX)
    num_blocks_y = num_blocks_1D(image_size.mValueY, block_size.mValueY)
    num_blocks_z = num_blocks_1D(image_size.mValueZ, block_size.mValueZ)
    num_blocks_c = num_blocks_1D(image_size.mValueC, block_size.mValueC)
    num_blocks_t = num_blocks_1D(image_size.mValueT, block_size.mValueT)
    
    block_index = IW.bpConverterTypesC_Index5D(0, 0, 0, 0, 0)
    for c in range(num_blocks_c):
        block_index.mValueC = c
        for t in range(num_blocks_t):
            block_index.mValueT = t
            for z in range(num_blocks_z):
                block_index.mValueZ = z
                for y in range(num_blocks_y):
                    block_index.mValueY = y
                    for x in range(num_blocks_x):
                        block_index.mValueX = x
                        block_index_ptr = IW.bpConverterTypesC_Index5DPtr(block_index)
                        cdll.bpImageConverterC_CopyBlockUInt8(imageconverter_ptr, voxel_data, block_index_ptr)
                        check_errors(cdll, imageconverter_ptr)
        
def get_channel_name(channel_index):
    if channel_index == 0:
        return 'First channel'
    elif channel_index == 1:
        return 'Second channel'
    elif channel_index == 2:
        return 'Third channel'
    else:
        return 'Other channel'

def create_parameter(name, value):
    return IW.bpConverterTypesC_Parameter(name.encode(), value.encode())
    
def get_parameters(num_channels):
    number_of_other_sections = 1 # Image
    number_of_sections = number_of_other_sections + num_channels
    parameter_section_data = (IW.bpConverterTypesC_ParameterSection * number_of_sections)()
    unit_parameter = IW.bpConverterTypesC_ParameterPtr(IW.bpConverterTypesC_Parameter(b'Unit', b'um'))
    image_parameter_section = IW.bpConverterTypesC_ParameterSection()
    image_parameter_section.mName = b'Image'
    image_parameter_section.mValues = unit_parameter
    image_parameter_section.mValuesCount = 1
    parameter_section_data[0] = image_parameter_section
    
    num_parameters_per_channel = 3
    for c in range(num_channels):
        section_index = number_of_other_sections + c
        
        channel_parameter_section = IW.bpConverterTypesC_ParameterSection()
        name_parameter = create_parameter('Name', get_channel_name(c))
        emission_parameter = create_parameter('LSMEmissionWavelength', str(700))
        other_parameter = create_parameter('OtherChannelParameter', 'OtherChannelValue')
        
        channel_parameter_data = (IW.bpConverterTypesC_Parameter * num_parameters_per_channel)()
        channel_parameter_data[0] = name_parameter
        channel_parameter_data[1] = emission_parameter
        channel_parameter_data[2] = other_parameter
        channel_parameter_section.mName = 'Channel {}'.format(c).encode()
        channel_parameter_section.mValues = channel_parameter_data
        channel_parameter_section.mValuesCount = num_parameters_per_channel
        parameter_section_data[section_index] = channel_parameter_section
        
    parameters = IW.bpConverterTypesC_ParametersPtr(IW.bpConverterTypesC_Parameters(parameter_section_data, number_of_sections))
    return parameters

def get_time_infos(num_time_infos):
    time_info_data = (IW.bpConverterTypesC_TimeInfo * num_time_infos)()
    
    julian_day = 2458885 # 5 feb 2020
    t = 0
    seconds = t + 4 + 60 * (27 + 60 * 15) # 3:27.04 PM + 1 sec per time point
    for t in range(num_time_infos):
        nanoseconds = (seconds + t) * int(1e9)
        time_info = IW.bpConverterTypesC_TimeInfo(julian_day, nanoseconds)
        time_info_data[t] = time_info
    return IW.bpConverterTypesC_TimeInfosPtr(IW.bpConverterTypesC_TimeInfos(time_info_data, num_time_infos))

def get_color_infos(num_color_infos):
    color_info_data = (IW.bpConverterTypesC_ColorInfo * num_color_infos)()
    for c in range(num_color_infos):
        color = IW.bpConverterTypesC_Color()
        color.mRed = 1 if (c % 3 == 0) else 0
        color.mGreen = 1 if (c % 3 == 1) else 0
        color.mBlue = 1 if (c % 3 == 2) else 0
        color.mAlpha = 1
        color_info = IW.bpConverterTypesC_ColorInfo()
        color_info.mIsBaseColorMode = True
        color_info.mBaseColor = color
        color_info.mColorTableSize = 0
        color_info.mOpacity = 0
        color_info.mRangeMin = 0
        color_info.mRangeMax = 255
        color_info.mGammaCorrection = 1
        color_info_data[c] = color_info
        
    return IW.bpConverterTypesC_ColorInfosPtr(IW.bpConverterTypesC_ColorInfos(color_info_data, num_color_infos))

def ProgressCallback(progress, total_bytes_written, user_data):
    data = IW.cast(user_data, IW.bpCallbackDataPtr)
    
    progress_percentage = int(progress * 100)
    if progress_percentage - data.contents.mProgress < 5:
        return
    
    image_index = data.contents.mImageIndex
    
    if total_bytes_written < 10 * 1024 * 1024:
        data_written = total_bytes_written / 1024
        unit = 'KB'
    else:
        data_written = total_bytes_written / (1024 * 1024)
        unit = 'MB'
    print('Progress image {}: {}% [{:.0f} {}]'.format(image_index, progress_percentage, data_written, unit))
    
    data.contents.mProgress = progress_percentage

bpConverterTypesC_ProgressCallback = IW.CFUNCTYPE(IW.c_void_p, IW.c_float, IW.c_ulonglong, IW.c_void_p)

callback_function = bpConverterTypesC_ProgressCallback(ProgressCallback)

def print_user_data(title, user_data):
    print('{} userdata progress: {}, image index: {}'.format(
    title,
    user_data.mProgress,
    user_data.mImageIndex))

def get_dll_filename():
    if platform.system() == 'Windows':
        return 'bpImarisWriter96.dll'
    elif platform.system() == 'Darwin':
        return 'libbpImarisWriter96.dylib'
    elif platform.system() == 'Linux':
        return 'libbpImarisWriter96.so'
    else:
        print('Platform not supported: "{}"'.format(platform.system()))
        return None
    
def test_convert(test_index):
    dll_filename = get_dll_filename()
    print('Loading dll: {}'.format(dll_filename))
    cdll = IW.CDLL(dll_filename)
    
    callback_userdata = IW.bpCallbackData()
    callback_userdata.mImageIndex = test_index
    output_filename = 'out_{}py.ims'.format(test_index)
    print('Writing {}'.format(output_filename))
    
    # bpImageConverterC_Create
    datatype = IW.bpConverterTypesC_UInt8Type
    image_size = get_image_size()
    image_extents = get_image_extents(image_size.contents)
    sample = get_sample()
    dimension_sequence = get_dimension_sequence()
    block_size = get_block_size()
    output_file = IW.c_char_p(output_filename.encode())
    options = get_options()
    application_name = IW.c_char_p(b'Imaris Writer Python')
    application_version = IW.c_char_p(b'0.1')
    progress_callback = callback_function
    
    cdll.bpImageConverterC_Create.restype = IW.bpImageConverterCPtr
    imageconverter_ptr = cdll.bpImageConverterC_Create(datatype, image_size, sample, dimension_sequence, block_size, output_file, options,
                                      application_name, application_version, progress_callback, IW.byref(callback_userdata))
    check_errors(cdll, imageconverter_ptr)
    
    # bpImageConverterC_CopyBlockUInt8
    copy_blocks(cdll, imageconverter_ptr, image_size.contents, block_size.contents)
    
    parameters = get_parameters(image_size.contents.mValueC)
    time_infos = get_time_infos(image_size.contents.mValueT)
    color_infos = get_color_infos(image_size.contents.mValueC)
    adjust_color_range = True
    
    # bpImageConverterC_Finish
    cdll.bpImageConverterC_Finish(imageconverter_ptr, image_extents, parameters, time_infos, color_infos, adjust_color_range)
    check_errors(cdll, imageconverter_ptr)
    
    # bpImageConverterC_Destroy
    cdll.bpImageConverterC_Destroy(imageconverter_ptr)
    

from datetime import datetime
def print_time(title, time):
    print('{} {}'.format(title, time.strftime("%H:%M:%S")))
    
def main():
    for i in range(1):
        start = datetime.now()
        print_time('start', start)
        test_convert(i)
        end = datetime.now()
        print_time('end', end)
        print('Duration {}'.format((end - start).seconds))
    print('Finished python writing test')


if __name__ == "__main__":
    main()
