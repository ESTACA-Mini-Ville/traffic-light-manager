FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3 \
    python3-pip \
    python3-dev \
    swig \
    libasio-dev \
    libtinyxml2-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install CMake 3.28
RUN wget https://github.com/Kitware/CMake/releases/download/v3.28.1/cmake-3.28.1-linux-x86_64.sh \
    && chmod +x cmake-3.28.1-linux-x86_64.sh \
    && ./cmake-3.28.1-linux-x86_64.sh --skip-license --prefix=/usr/local \
    && rm cmake-3.28.1-linux-x86_64.sh

WORKDIR /tmp

# Install Foonathan Memory
RUN git clone https://github.com/foonathan/memory.git \
    && cd memory \
    && mkdir build && cd build \
    && cmake .. -DCMAKE_POSITION_INDEPENDENT_CODE=ON -DFOONATHAN_MEMORY_BUILD_EXAMPLES=OFF -DFOONATHAN_MEMORY_BUILD_TESTS=OFF \
    && make -j$(nproc) && make install

# Install Fast CDR
RUN git clone https://github.com/eProsima/Fast-CDR.git \
    && cd Fast-CDR \
    && mkdir build && cd build \
    && cmake .. \
    && make -j$(nproc) && make install

# Install Fast DDS
RUN git clone https://github.com/eProsima/Fast-DDS.git \
    && cd Fast-DDS \
    && mkdir build && cd build \
    && cmake .. -DTHIRDPARTY=ON -DSECURITY=ON \
    && make -j$(nproc) && make install

# Install Fast DDS Python
RUN git clone https://github.com/eProsima/Fast-DDS-python.git \
    && cd Fast-DDS-python/fastdds_python \
    && mkdir build && cd build \
    && cmake .. \
    && make -j$(nproc) && make install

# Install Java for fastddsgen
#RUN apt-get update && apt-get install -y default-jre && rm -rf /var/lib/apt/lists/*
RUN apt update && apt install -y \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*


# Install fastddsgen
RUN git clone --recursive https://github.com/eProsima/Fast-DDS-Gen.git \
    && cd Fast-DDS-Gen \
    && ./gradlew assemble \
    && mkdir -p /usr/local/share/fastddsgen/java \
    && cp build/libs/fastddsgen.jar /usr/local/share/fastddsgen/java/ \
    && cp scripts/fastddsgen /usr/local/bin/

# Update library path
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH=/usr/local/lib/python3.10/site-packages:/usr/local/lib/python3.10/dist-packages:$PYTHONPATH

WORKDIR /app

COPY requirements.txt .
# RUN pip3 install --no-cache-dir -r requirements.txt

COPY src/ ./src/

COPY types ./src/types

# Generate and compile IDL Python code
RUN cd src/types \
    # Rename types.idl to idl_types.idl to avoid shadowing Python stdlib `types` module
    && mv types.idl idl_types.idl \
    && fastddsgen -python idl_types.idl \
    # Ensure generated headers in sub-folders are visible to the compiler (SWIG wrapper includes plain header names)
    && cmake . -DCMAKE_CXX_FLAGS="-I$(pwd) -I$(pwd)/miniville_msgs -I$(pwd)/geometry_msgs -I$(pwd)/std_msgs" \
    && cmake --build . \
    && cp *.py .. \
    && cp *.so ..

CMD ["python3", "-u", "src/main.py"]
