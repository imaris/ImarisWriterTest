# ImarisWriterTest

Test project for ImarisWriter library.

### Dependencies

1. ImarisWriter: https://github.com/imaris/ImarisWriter

### Build and run

- C++ test program
  
  ```bash
  cd application
  
  g++ -I. -I<parent_dir_of_ImarisWriter> -L<parent_dir_of_ImarisWriter>/lib -o ImarisWriterTestRelease ImarisWriterTest.cxx -lbpImarisWriter96 -lpthread

  ./ImarisWriterTestRelease -sizex 400 -sizey 400 -sizez 100 -sizet 1 -sizec 1 -type 16bit -threads 8 -outputpath out -randseed 33 -compression 31 img.ims
  ```

  Debug version can be compiled with additional flags:

  ```bash
  g++ -I. -I<parent_dir_of_ImarisWriter> -L<parent_dir_of_ImarisWriter>/lib -O0 -g -DDEBUG -D_DEBUG -o ImarisWriterTestDebug ImarisWriterTest.cxx -lbpImarisWriter96 -lpthread
  ```

- C test program
  
  ```bash
  cd testC

  gcc -I<parent_dir_of_ImarisWriter> -L<parent_dir_of_ImarisWriter>/lib -o bpImarisWriter96TestProgram bpImarisWriter96TestProgram.c -lbpImarisWriter96 -lpthread

  ./bpImarisWriter96TestProgram
  ```
  
