# Virtual-Graffiti

This Project is only tested on Ubuntu 22.04

# Installation
## How to install OpenCV 4.6.0 with CUDA 11.7.1 and CUDNN 8.5.0.96 in Ubuntu 22.04

## 1. Install required libraries
### 1.1. First of all install update and upgrade your system:
```
$ sudo apt update
$ sudo apt upgrade
```
   
    
### 1.2. Then, install required libraries:
* Generic tools:
    ```
    $ sudo apt install build-essential cmake pkg-config unzip yasm git checkinstall -y
    ```
* Image I/O libs
    ``` 
    $ sudo apt install libjpeg-dev libpng-dev libtiff-dev -y
    ``` 
* Video/Audio Libs - FFMPEG, GSTREAMER, x264 and so on.
    ```
    $ sudo apt install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev -y
    $ sudo apt install libxvidcore-dev x264 libx264-dev libfaac-dev libmp3lame-dev libtheora-dev -y
    $ sudo apt install libfaac-dev libmp3lame-dev libvorbis-dev -y
    ```
* OpenCore - Adaptive Multi Rate Narrow Band (AMRNB) and Wide Band (AMRWB) speech codec
    ```
    $ sudo apt install libopencore-amrnb-dev libopencore-amrwb-dev -y
    ```
    
* Cameras programming interface libs
    ```
    $ sudo apt-get install libdc1394-25 libxine2-dev libv4l-dev v4l-utils -y
    $ cd /usr/include/linux
    $ sudo ln -s -f ../libv4l1-videodev.h videodev.h
    $ cd ~
    ```

* GTK lib for the graphical user functionalites coming from OpenCV highghui module 
    ```
    $ sudo apt-get install libgtk-3-dev -y
    ```
* Python libraries for python3:
    ```
    $ sudo apt-get install python3-dev python3-pip -y
    $ sudo -H pip3 install -U pip numpy
    $ sudo apt install python3-testresources -y
    ```
* Parallelism library C++ for CPU
    ```
    $ sudo apt-get install libtbb-dev -y
    ```
* Optimization libraries for OpenCV
    ```
    $ sudo apt-get install libatlas-base-dev gfortran -y
    ```
* Optional libraries:
    ```
    $ sudo apt-get install libprotobuf-dev protobuf-compiler -y
    $ sudo apt-get install libgoogle-glog-dev libgflags-dev -y
    $ sudo apt-get install libgphoto2-dev libeigen3-dev libhdf5-dev doxygen -y
    ```

### 1.3. Install Nvidia driver:
```
$ sudo apt install nvidia-driver-515 nvidia-dkms-515 -y
```

### 1.4. Install cuda (https://developer.nvidia.com/cuda-downloads)
```
$ wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
$ sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
$ wget https://developer.download.nvidia.com/compute/cuda/11.7.1/local_installers/cuda-repo-ubuntu2204-11-7-local_11.7.1-515.65.01-1_amd64.deb
$ sudo dpkg -i cuda-repo-ubuntu2204-11-7-local_11.7.1-515.65.01-1_amd64.deb
$ sudo cp /var/cuda-repo-ubuntu2204-11-7-local/cuda-*-keyring.gpg /usr/share/keyrings/
$ sudo apt-get update
$ sudo apt-get -y install cuda
$ sudo reboot 0
```

### 1.5. Install cuDNN (https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html)
```
$ sudo apt-get install zlib1g
```
* Downloade cuDNN
    * In order to download cuDNN, ensure you are registered for the NVIDIA Developer Program.
    Procedure

    * Go to: NVIDIA cuDNN home page: https://developer.nvidia.com/cudnn.
    * Click Download.
    * Complete the short survey and click Submit.
    * Accept the Terms and Conditions. A list of available download versions of cuDNN displays.
    * Select the cuDNN version that you want to install. A list of available resources displays.

* Before issuing the following commands, you must replace X.Y and 8.x.x.x with your specific CUDA and cuDNN versions. Navigate to your <cudnnpath> directory containing the cuDNN Debian local installer file.
    ```
    $ sudo dpkg -i cudnn-local-repo-${OS}-8.x.x.x_1.0-1_amd64.deb
    ```

* Import the CUDA GPG key.
    ```
    $ sudo cp /var/cudnn-local-repo-*/cudnn-local-*-keyring.gpg /usr/share/keyrings/
    ```

* Refresh the repository metadata.
    ```
    $ sudo apt-get update
    ```

* Install the runtime library.
    ```
    $ sudo apt-get install libcudnn8=8.x.x.x-1+cudaX.Y
    ```

* Install the developer library.
    ```
    $ sudo apt-get install libcudnn8-dev=8.x.x.x-1+cudaX.Y
    ```

* Install the code samples and the cuDNN library documentation.
    ```
    $ sudo apt-get install libcudnn8-samples=8.x.x.x-1+cudaX.Y
    ```

## 2.0. Compile and install OpenCV with Cuda and cuDNN
* We will now proceed with the installation (see the Qt flag that is disabled to do not have conflicts with Qt5.0).
    ```
    $ cd ~/Downloads
    $ wget -O opencv.zip https://github.com/opencv/opencv/archive/refs/tags/4.6.0.zip
    $ wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/refs/tags/4.6.0.zip
    $ unzip opencv.zip
    $ unzip opencv_contrib.zip
    ```

* Create a virtual environtment for the python binding module (OPTIONAL)
    ```
    $ sudo pip install virtualenv virtualenvwrapper
    $ sudo rm -rf ~/.cache/pip
    ```

* Edit ~/.bashrc
    ```
    $ export WORKON_HOME=$HOME/.virtualenvs
    $ export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
    $ source /usr/local/bin/virtualenvwrapper.sh
    $ mkvirtualenv cv -p python3
    $ pip install numpy
    ```
* Procced with the installation
    ```
    $ cd opencv-4.6.0
    $ mkdir build
    $ cd build

    cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D WITH_TBB=ON \
    -D ENABLE_FAST_MATH=1 \
    -D CUDA_FAST_MATH=1 \
    -D WITH_CUBLAS=1 \
    -D WITH_CUDA=ON \
    -D BUILD_opencv_cudacodec=OFF \
    -D WITH_CUDNN=ON \
    -D OPENCV_DNN_CUDA=ON \
    -D CUDA_ARCH_BIN=6.1 \
    -D WITH_V4L=ON \
    -D WITH_QT=OFF \
    -D WITH_OPENGL=ON \
    -D WITH_GSTREAMER=ON \
    -D OPENCV_GENERATE_PKGCONFIG=ON \
    -D OPENCV_PC_FILE_NAME=opencv.pc \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D OPENCV_PYTHON3_INSTALL_PATH=~/.virtualenvs/cv/lib/python3.10/site-packages \
    -D PYTHON_EXECUTABLE=~/.virtualenvs/cv/bin/python \
    -D OPENCV_EXTRA_MODULES_PATH=~/Downloads/opencv_contrib-4.6.0/modules \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D INSTALL_C_EXAMPLES=OFF \
    -D BUILD_EXAMPLES=OFF ..
    ```
    
    * To use CUDNN you must modify those flags (to set the correct value of CUDA_ARCH_BIN you must visit https://developer.nvidia.com/cuda-gpus and find the Compute Capability CC of your graphic card). Then write the correct version in CUDA_ARCH_BIN. For example: for the GTX 1060 it would be 6.1
        ```
            ...
            -D WITH_CUDNN=ON \
            -D OPENCV_DNN_CUDA=ON \
            -D CUDA_ARCH_BIN=6.1 \
            ...
        ```

* Before the compilation you must check that CUDA has been enabled in the configuration summary printed on the screen. (If you have problems with the CUDA Architecture go to the end of the document).
    ```
    ...
    --   NVIDIA CUDA:                   YES (ver 11.7, CUFFT CUBLAS FAST_MATH)
    --     NVIDIA GPU arch:             75
    --     NVIDIA PTX archs:
    -- 
    --   cuDNN:                         YES (ver 8.5.0)
    ...
    ```

* If it is fine proceed with the compilation (Use nproc to know the number of cpu cores):
   ``` 
    $ nproc
    $ make -j8
    $ sudo make install
    ```

* Include the libs in your environment    
    ```
    $ sudo /bin/bash -c 'echo "/usr/local/lib" >> /etc/ld.so.conf.d/opencv.conf'
    $ sudo ldconfig
    ```

* If you want to have available opencv python bindings in the system environment you should copy the created folder during the installation of OpenCV (* -D OPENCV_PYTHON3_INSTALL_PATH=~/.virtualenvs/cv/lib/python3.10/site-packages *) into the *dist-packages* folder of the target python interpreter:
    ```
    $ sudo cp -r ~/.virtualenvs/cv/lib/python3.10/site-packages/cv2 /usr/local/lib/python3.10/dist-packages
    ```
    * Modify config-3.10.py to point to the target directory"
        ```
        $ sudo nano /usr/local/lib/python3.10/dist-packages/cv2/config-3.10.py 
        ```
        ``` 
        PYTHON_EXTENSIONS_PATHS = [
            os.path.join('/usr/local/lib/python3.10/dist-packages/cv2', 'python-3.10')
        ] + PYTHON_EXTENSIONS_PATHS
        ``` 


## 3.0 EXAMPLE TO TEST OPENCV 4.5.2 with GPU in C++

* Verify the installation by compiling and executing the following example:
    ```c++
    #include <iostream>
    #include <ctime>
    #include <cmath>
    #include "bits/time.h"

    #include <opencv2/core.hpp>
    #include <opencv2/highgui.hpp>
    #include <opencv2/imgproc.hpp>
    #include <opencv2/imgcodecs.hpp>

    #include <opencv2/core/cuda.hpp>
    #include <opencv2/cudaarithm.hpp>
    #include <opencv2/cudaimgproc.hpp>

    #define TestCUDA true

    int main() {
        try {
            cv::String filename = "picture.jpg";
            cv::Mat srcHost = cv::imread(filename, cv::IMREAD_GRAYSCALE);

            std::clock_t cpu_begin = std::clock();
            for(int i=0; i<1000; i++) {
                cv::Mat dst;
                cv::bilateralFilter(srcHost,dst,3,1,1);
            }
            std::clock_t cpu_end = std::clock();

            std::clock_t gpu_begin = std::clock();
            for(int i=0; i<1000; i++) {
                cv::cuda::GpuMat dst, src;
                src.upload(srcHost);

                //cv::cuda::threshold(src,dst,128.0,255.0, CV_THRESH_BINARY);
                cv::cuda::bilateralFilter(src,dst,3,1,1);

                cv::Mat resultHost;
                dst.download(resultHost);
            }
            std::clock_t gpu_end = std::clock();

            //cv::imshow("Result",resultHost);
            //cv::waitKey();

            std::cout << "CPU: " << double(cpu_end-cpu_begin) / CLOCKS_PER_SEC  << std::endl;
            std::cout << "GPU: " << double(gpu_end-gpu_begin) / CLOCKS_PER_SEC  << std::endl;

        } catch(const cv::Exception& ex) {
            std::cout << "Error: " << ex.what() << std::endl;
        }
    }
    ```
* Compile and execute:
    ```
    $ g++ test.cpp `pkg-config opencv --cflags --libs` -o test
    $ ./test`
    ```


## 4.0. Setup Virtual-Graffiti
```
$ pip install mouse
```
### 4.1. Run Virtual-Graffiti
```
$ sudo python Main.py
```

# Source
- [OpenCV]https://www.youtube.com/watch?v=
- [raulqf/Install_OpenCV4_CUDA11_CUDNN8]https://gist.github.com/raulqf/f42c718a658cddc16f9df07ecc627be7