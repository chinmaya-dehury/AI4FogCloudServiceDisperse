# install necessary packages
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y \
    build-essential \
    cmake \
    pkg-config \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libfontconfig1-dev \
    libcairo2-dev \
    libgdk-pixbuf2.0-dev \
    libpango1.0-dev \
    libgtk2.0-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    libqt5gui5 \
    libqt5webkit5 \
    libqt5test5 \
    python3-pyqt5 \
    python3-dev \
    wget \
    unzip \
    ffmpeg

# enter in "input" folder
mkdir input
cd input/

# download "app1_video_long.mp4"
FILEID="1uX_g9OQJE6L0ZD_1HO8hNPeZyqcARLzJ"
FILENAME="app1_video_long.mp4"
FILEURL="https://docs.google.com/uc?export=download&id=$FILEID"
if [ -f "$FILENAME" ]; then
    echo "$FILENAME exists."
else
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate ${FILEURL} -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=$FILEID" -O $FILENAME && rm -rf /tmp/cookies.txt
fi

# download "app2_audio_long.mp3"
FILEID="1yRmwiTLj-43W7CS3rRfysaeb0mPGGsmq"
FILENAME="app2_audio_long.mp3"
FILEURL="https://docs.google.com/uc?export=download&id=$FILEID"
if [ -f "$FILENAME" ]; then
    echo "$FILENAME exists."
else
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate ${FILEURL} -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=$FILEID" -O $FILENAME && rm -rf /tmp/cookies.txt
fi

# download "app3_audio_long.mp3"

# exit from "input" folder
cd ../

# download "torch_libs.zip"
FILEID="1jfjhdm6mcsMxrncUPYI8C05mMqHldzdO"
FILENAME="torch_libs.zip"
FILEURL="https://docs.google.com/uc?export=download&id=$FILEID"
if [ -f "$FILENAME" ]; then
    echo "$FILENAME exists."
else
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate ${FILEURL} -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=$FILEID" -O $FILENAME && rm -rf /tmp/cookies.txt
    unzip torch_libs.zip -d torch_libs
fi

# download "state_spaces.zip"
FILEID="1_VB_Qh_8kxH0uqdO_64ITJlyfFkwdqxb"
FILENAME="state_spaces.zip"
FILEURL="https://docs.google.com/uc?export=download&id=$FILEID"
if [ -f "$FILENAME" ]; then
    echo "$FILENAME exists."
else
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate ${FILEURL} -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=$FILEID" -O $FILENAME && rm -rf /tmp/cookies.txt
    unzip state_spaces.zip -d state_spaces
fi

# set virtualenv
python3 -m pip install virtualenv
python3 -m virtualenv env
source env/bin/activate

# install pip packages
pip3 install --upgrade pip
pip3 install -r requirements.txt
pip3 install torch_libs/torch_libs/torch-1.8.0a0+37c1f4a-cp39-cp39-linux_aarch64.whl
pip3 install torch_libs/torch_libs/torchvision-0.9.0a0+01dfa8e-cp39-cp39-linux_aarch64.whl
