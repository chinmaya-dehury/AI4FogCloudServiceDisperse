# install necessary packages
sudo apt update -y && sudo apt upgrade -y
sudo apt install -y \
    python3-pyqt5 \
    python3-dev \
    wget


# download input audio
mkdir input/input2
cd input/input2
FILEID="1yRmwiTLj-43W7CS3rRfysaeb0mPGGsmq"
FILENAME="movie_audio.mp3"
FILEURL="https://docs.google.com/uc?export=download&id=$FILEID"
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate ${FILEURL} -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=$FILEID" -O $FILENAME && rm -rf /tmp/cookies.txt

cd ../..

# download output video
mkdir output/output2
cd output/output2
FILEID="1NvZMoX2Xy3G1T1zx7J6MyavIFT2dEe9g"
FILENAME="video.mp4"
FILEURL="https://docs.google.com/uc?export=download&id=$FILEID"
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate ${FILEURL} -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=$FILEID" -O $FILENAME && rm -rf /tmp/cookies.txt

# ending download, back to previous folder
cd ../..

# set virtualenv
python3 -m pip install virtualenv
python3 -m virtualenv env
source env/bin/activate

# install pip packages
pip3 install --upgrade pip
pip3 install -r requirements.txt
