CC = g++
CUCC = nvcc -m64 -ccbin $(CC)
TARGET = sqdtrt

TRIPLE?=x86_64-linux
CUDA_INSTALL_DIR = /usr/local/cuda-8.0
CUDNN_INSTALL_DIR = /usr/local/cuda-8.0
CUDA_LIBDIR = lib
CUDNN_LIBDIR = lib64
INCPATHS    =-I"$(CUDA_INSTALL_DIR)/include" -I"/usr/local/include" -I"../include" -I"../common" -I"$(CUDNN_INSTALL_DIR)/include" -I"../../include" $(TGT_INCLUDES)
LIBPATHS    =-L"$(CUDA_INSTALL_DIR)/targets/$(TRIPLE)/$(CUDA_LIBDIR)" -L"/usr/local/lib" -L"../lib" -L"$(CUDA_INSTALL_DIR)/$(CUDA_LIBDIR)" -L"$(CUDNN_INSTALL_DIR)/$(CUDNN_LIBDIR)" -L"../../lib" $(TGT_LIBS)

# COMMON_LIBS = -lcudnn -lcublas -lcudart_static -lnvToolsExt -lcudart
COMMON_LIBS = -lcudnn -lcudart -lcudart_static
# LIBS  =-lnvinfer -lnvparsers -lnvinfer_plugin $(COMMON_LIBS)
# DLIBS =-lnvinfer -lnvparsers -lnvinfer_plugin $(COMMON_LIBS)
LIBS  =-lnvinfer -lnvinfer_plugin $(COMMON_LIBS)
DLIBS =-lnvinfer -lnvinfer_plugin $(COMMON_LIBS)

COMMON_FLAGS += -std=c++11 $(INCPATHS) `pkg-config --cflags --libs opencv`
CFLAGS=$(COMMON_FLAGS)
CFLAGSD=$(COMMON_FLAGS) -g

COMMON_LD_FLAGS += $(LIBPATHS) -L$(OUTDIR)
LFLAGS=$(COMMON_LD_FLAGS)
LFLAGSD=$(COMMON_LD_FLAGS)

$(TARGET): testTrt.o common.o trtUtil.o tensorUtil.o tensorCuda.o
	$(CC) -Wall testTrt.o common.o trtUtil.o tensorUtil.o tensorCuda.o -o $(TARGET) $(CFLAGSD) $(LIBPATHS) $(LIBS)
testTrt.o: testTrt.cpp tensorUtil.h tensorCuda.h common.h
	$(CUCC) -c testTrt.cpp $(CFLAGSD) $(LFLAGSD) $(LIBS)
common.o: common.cpp common.h
	$(CUCC) -c common.cpp $(CFLAGSD) $(LFLAGSD) $(LIBS)
trtUtil.o: trtUtil.cpp trtUtil.h
	$(CUCC) -c trtUtil.cpp $(CFLAGSD) $(LFLAGSD) $(LIBS)
tensorUtil.o: tensorUtil.cu tensorUtil.h tensorCuda.h
	$(CUCC) -c tensorUtil.cu $(CFLAGSD) $(LFLAGSD) $(LIBS)
tensorCuda.o: tensorCuda.cu tensorCuda.h
	$(CUCC) -c tensorCuda.cu $(CFLAGSD) $(LFLAGSD) $(LIBS)

clean:
	rm -f *.o