
TEMPLATE = subdirs
CONFIG += ordered
CONFIG += debug_and_release
SUBDIRS += ImarisWriter ImarisWriterTest

ImarisWriter.file = ../../../libs/ImarisWriter/project/qt/ImarisWriter.pro
ImarisWriterTest.file = ../project/qt/ImarisWriterTest.pro
ImarisWriterTest.depends = ImarisWriter
