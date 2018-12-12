from FCI.PrefixInt import DoublingLengthCode, DoublingLengthDecode, Binary
import numpy as np
import os
import cv2
from PIL import Image
import webcam
import pickle
import sys

testImg = np.asarray([[0, 255], [255, 0]])

def readLength(BIG_STR):
    BinLength = ''
    BinN1 = iter(BIG_STR)
    nbits = 0
    for B in BinN1:
        BinLength += B
        nbits = nbits + 2
        try:
            if next(BinN1) != B:    break   # consumes the next bit
        except Exception as e:
            # print("REACHED END OF STRING")
            pass
    if BinLength is not '':
        Length = int(BinLength, 2)
    else:
        Length = 0
    return Length, nbits

def readSequenceOfDoublingCodes(BIG_STR, current_pos=0, return_only=None):
    # print("DECODING:%s"%BIG_STR)
    ret = []
    pos = current_pos
    length = 0
    nbits = 0
    while(pos<len(BIG_STR)):
        length, nbits = readLength(BIG_STR[pos:])
        pos = pos + nbits
        if pos + length < len(BIG_STR):
            number_decoded = int(BIG_STR[pos:pos+length],2)
            # print("Decoding length:%s, number:%s"%(str(length), str(number_decoded)))
            ret.append(number_decoded)
        pos = pos + length
        if(return_only and len(ret)==return_only):
            # print("RETURN_ONLY SATISFIED returning", ret, pos)
            return ret, pos

    return ret, len(BIG_STR)



def prepareBigDoublingSequence(arr):
    bigstr = ''
    for item in arr:
        bigstr += DoublingLengthCode(int(item))
    z = DoublingLengthCode(arr[-1])
    return bigstr

# Expects a black & white image (2D numpy array)
def imageToDoubling(img):
    rows, cols = img.shape
    # rowcode = DoublingLengthCode(rows)
    # colcode = DoublingLengthCode(cols)
    ret = []
    ret.append(rows)
    ret.append(cols)
    flat = img.flatten().tolist()
    return prepareBigDoublingSequence(ret + flat)

def imageToDoubling(img):
    rows, cols = img.shape
    # rowcode = DoublingLengthCode(rows)
    # colcode = DoublingLengthCode(cols)
    ret = []
    ret.append(rows)
    ret.append(cols)
    flat = img.flatten().tolist()
    return prepareBigDoublingSequence(ret + flat)



def doublingToImage(BIG_STR):
    arr, _ = readSequenceOfDoublingCodes(BIG_STR)
    rows = arr[0]
    cols = arr[1]
    img = np.reshape(arr[2:], (rows, cols))
    img2 = img[:]
    img2.astype(int)
    return img2

def writeGifToDoubling(giffile, outfile = "gif_doubling"):
    seq = gifToDoubling(giffile)
    retsize = writeSequenceToBinary(seq, outfile)
    return retsize

def writeGifToDoublingDifference(giffile, outfile = "gif_doubling_difference"):
    seq = gifToDoublingWithDifference(giffile)
    retsize = writeSequenceToBinary(seq, outfile)
    return retsize

def gifToDoubling(giffile):
    # Need to read sequence of images
    images = webcam.split_gif(giffile)
    pickle.dump(images, open("gif_pickle", "wb"))
    sequenceLength = len(images)
    ret = []
    if sequenceLength > 0:
        rows, cols = images[0].shape
        ret.append(sequenceLength)
        ret.append(rows)
        ret.append(cols)
    for image in images:
        flat = image.flatten().tolist()
        ret = ret + flat
    return prepareBigDoublingSequence(ret)

def doublingToGif(infile="gif_doubling"):
    # Reading images now
    seq = readSequenceFromBinary(infile)
    arr,_ = readSequenceOfDoublingCodes(seq)
    sequenceLength = arr[0]
    rows = arr[1]
    cols = arr[2]
    imagesize = rows * cols
    ptr = 3
    images = []
    while (ptr+imagesize <= len(arr)):
        images.append(np.reshape(arr[ptr:ptr+imagesize], (rows, cols)))
        ptr = ptr+imagesize
    pickle.dump(images, open("gif_decoded_pickle", "wb"))
    webcam.create_gif(images, 1 ,"gif_decoded.gif")
    return os.path.getsize("gif_decoded.gif")

def gifToDoublingWithDifference(giffile):
    # Need to read sequence of images
    images = webcam.split_gif(giffile)
    # print(images[0] - images[1])
    pickle.dump(images, open("gif_pickle", "wb"))
    sequenceLength = len(images)
    ret = []
    if sequenceLength > 0:
        rows, cols = images[0].shape
        ret.append(sequenceLength)
        ret.append(rows)
        ret.append(cols)
    image_index = 0
    first_image = None
    seq = prepareBigDoublingSequence(ret)
    for image in images:
        if image_index == 0:
            first_image = image.flatten()
            flat = first_image.tolist()
            # print("SEQ LENGTH BEFORE FIRST IMAGE=", len(seq))
            seq+=prepareBigDoublingSequence(flat)
            # print("SEQ LENGTH AFTER FIRST IMAGE=", len(seq))
        else:

            current_image = image.flatten()
            difference = first_image - current_image
            for bit in difference:
                if bit < 0:
                    temp = '1'+DoublingLengthCode(-bit)
                    seq+=temp
                else:
                    temp = '0'+DoublingLengthCode(bit)
                    seq+=temp
            first_image = current_image
        image_index += 1
    return seq

def doublingToGifWithDifference(infile="gif_doubling_difference"):
    # Reading images now
    seq = readSequenceFromBinary(infile)
    arr, pos = readSequenceOfDoublingCodes(seq, return_only = 3)
    sequenceLength = arr[0]
    rows = arr[1]
    cols = arr[2]
    imagesize = rows * cols
    # print("BEFORE FIRST IMAGE:", pos)
    arrfirstimage, pos2 = readSequenceOfDoublingCodes(seq[pos:], return_only = imagesize)
    # print("AFTER FIRST IMAGE:", pos2 + pos)
    pos2 = pos2 + pos
    arr = readBitSeparatedSequenceOfDoublingCodes(seq[pos2:])
    arr = arrfirstimage + arr
    ptr = 0
    images = []
    image_index = 0
    first_image = None
    while (ptr+imagesize <= len(arr)):
        if image_index == 0:
            first_image = np.reshape(arr[ptr:ptr+imagesize], (rows, cols))
            # print(first_image)
            images.append(first_image)
        else:
            difference = np.reshape(arr[ptr:ptr+imagesize], (rows, cols))
            current_image = first_image - difference
            # print(current_image)
            images.append(current_image)
            first_image = current_image
        ptr = ptr+imagesize
        image_index += 1
    pickle.dump(images, open("gif_decoded_pickle_difference", "wb"))
    webcam.create_gif(images, 1 ,"gif_decoded_difference.gif")
    return os.path.getsize("gif_decoded_difference.gif")

def readBitSeparatedSequenceOfDoublingCodes(BIG_STR, current_pos=0):
    # print("DECODING:%s"%BIG_STR)
    ret = []
    pos = current_pos
    length = 0
    nbits = 0
    while(pos<len(BIG_STR)):
        sign = 1 if BIG_STR[pos]=="0" else -1
        pos = pos+1
        length, nbits = readLength(BIG_STR[pos:])
        pos = pos + nbits
        if pos + length < len(BIG_STR):
            # print(pos, length, BIG_STR[pos:pos+length])
            try:
                number_decoded = int(BIG_STR[pos:pos+length],2)
                # print("Decoding length:%s, number:%s"%(str(length), str(number_decoded)))
                ret.append(sign*number_decoded)
            except Exception as e:
                pass
                # print(sign, length,nbits,e, pos)
        pos = pos + length
    return ret

def sequenceToBinary(BIG_STR):
    bin_arr = []
    ind = 0
    while(ind+8< len(BIG_STR)):
        bin_arr.append(int(BIG_STR[ind:ind+8],2))
        ind = ind+8
    if ind <= len(BIG_STR) -1:
        op = BIG_STR[ind:]
        appending = (8-len(op))*"0"
        bin_arr.append(int(BIG_STR[ind:]+appending, 2))
    return bytes(bin_arr)

def binaryToSequence(byts):
    seq = ''
    for item in byts:
        length = len(Binary(item))
        seq += (8-length)*"0" + Binary(item)
    return seq
# bigstr = rows+cols + a*2 + b*3
# readSequenceOfDoublingCodes(bigstr)

def writeSequenceToBinary(BIG_STR, filename="image_doubling"):
    with open(filename, "wb") as fo:
        fo.write(sequenceToBinary(BIG_STR))
    return os.path.getsize(filename)

def readSequenceFromBinary(filename="image_doubling"):
    ret = None
    with open(filename, "rb") as fo:
        ret = fo.read()
    return binaryToSequence(ret)

def writeNumpyImage(img, filename="image_numpy"):
    np.save(open(filename, "wb"), img)
    return os.path.getsize(filename)

def readNumpyImage(filename="image_numpy"):
    img = np.load(filename)
    return img

def getImageSequence(imagefile):
    # img = prepareImage(imagefile)
    img = np.asarray(Image.open(imagefile))
    img = np.reshape(img.flatten().tolist(), img.shape)
    img = img.astype(int)
    imgseq = imageToDoubling(img)
    return imgseq, img


# Final Image encoding and decoding functions
def encodeImage(imagefile, outfile="image_doubling"):
    imgseq, img = getImageSequence(imagefile)
    originalsize = writeNumpyImage(img)
    outsize = writeSequenceToBinary(imgseq, outfile)
    print("-"*20, "[ ENCODING %s ]"%imagefile, "-"*20)
    print("ENCODED SIZE:%s"%(str(outsize)))
    print("-"*20, "[ DONE ]", "-"*20)

def decodeImage(encodedfile="image_doubling", outfile="image_decoded"):
    imgseq = readSequenceFromBinary(encodedfile)
    img = doublingToImage(imgseq)
    print("-"*20, "[ DECODING %s ]"%encodedfile, "-"*20)
    print("ENCODED SIZE:", os.path.getsize(encodedfile))
    print("DECODED IMAGE SIZE:", writeNumpyImage(np.asarray(img), outfile), "bytes")
    print("-"*20, "[ DONE ]", "-"*20)

# Final usable 
def createDoublingGif(giffile = "webcam.gif"):
    print("="*20, "[ Creating DoublingCode for < %s > ]"%giffile, "="*20)
    writeGifToDoubling(giffile)
    doublingToGif("gif_doubling")
    print("\/ All sizes in bytes \/")
    print("ENCODED:", os.path.getsize("gif_doubling"),"< gif_doubling >")
    print("ORIGINAL(numpy image-list pickle):", os.path.getsize("gif_pickle"),"< gif_pickle >")
    print("DECODED:", os.path.getsize("gif_decoded_pickle"), "< gif_decoded_pickle >")

def compressGifLossless(giffile = "webcam.gif"):
    createDoublingGif(giffile)
    print("="*20, "[ Lossless-Compression using difference values < %s > ]"%giffile, "="*20)
    writeGifToDoublingDifference(giffile)
    doublingToGifWithDifference("gif_doubling_difference")
    print("\/ All sizes in bytes \/")
    print("ENCODED:", os.path.getsize("gif_doubling_difference"), "< gif_doubling_difference >")
    print("ORIGINAL(numpy image-list pickle):", os.path.getsize("gif_pickle"), "< gif_pickle >")
    print("DECODED:", os.path.getsize("gif_decoded_pickle_difference"), "< gif_decoded_pickle_difference >")
    lossless_size = os.path.getsize("gif_doubling_difference")
    doubling_size = os.path.getsize("gif_doubling")
    compression = 100*(doubling_size - lossless_size)/doubling_size
    print("[ COMPRESSION with respect to DoubleCoded GIF = (%s - %s)/%s = %.2f percent ]" % (doubling_size, lossless_size, doubling_size, compression))


def main():
    if len(sys.argv) > 1:
        compressGifLossless(sys.argv[1])
    else:
        compressGifLossless()

if __name__ == "__main__":
    main()
