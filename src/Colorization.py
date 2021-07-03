"""
This Image Colorization method uses Zhang, R.'s pretrained CNN model trained on the CAFFE framework
and the .prototxt file containing the structural information of the CNN
Caffe Model Link: http://eecs.berkeley.edu/~rich.zhang/projects/2016_colorization/files/demo_v2/colorization_release_v2.caffemodel
Prototxt Link: https://github.com/richzhang/colorization/blob/caffe/models/colorization_deploy_v2.prototxt
and also the pretrained Cluster Center in the .npy file format
Cluster Center Link: https://github.com/richzhang/colorization/blob/caffe/resources/pts_in_hull.npy

http://richzhang.github.io/colorization/ 
@inproceedings{zhang2016colorful,
  title={Colorful Image Colorization},
  author={Zhang, Richard and Isola, Phillip and Efros, Alexei A},
  booktitle={ECCV},
  year={2016}
}

Modified of Reference Source Code retrieved from:
1. TheCodingBug. (2021, February 1). Video & Image Colorization Using OpenCV Python | AI COLORIZATION 
   FOR IMAGES & VIDEOS [Video].Retrieved from https://www.youtube.com/watch?v=EZWHAd0IH1M
2. OpenCV. samples/dnn/colorization.cpp. Retrieved from https://docs.opencv.org/4.5.2/d6/d39/samples_2dnn_2colorization_8cpp-example.html
"""

import cv2 as cv
import numpy as np
from os import path
import json
import re
from tqdm import tqdm

class Colorization:

    def __init__(self, inputPath, inputData = "image"):
        self.inputPath = inputPath

        # Set the file path to the pretrained model
        with open("settings.json") as file:
            data = json.load(file)
            self.modelPath = data["modelPath"]
            self.prototxtPath = data["prototxtPath"]
            self.clusterPath = data["clusterPath"]

        # Using OpenCV's Deep Neural Network Module to load the model
        self.net = cv.dnn.readNetFromCaffe(self.prototxtPath, self.modelPath)
        # Using numpy to load the pretrained cluster centers
        pts_in_hull = np.load(self.clusterPath)
        # Populate the ab cluster centers as 1x1 convolution kernel
        pts_in_hull = pts_in_hull.transpose().reshape(2, 313, 1, 1)
        self.net.getLayer(self.net.getLayerId("class8_ab")).blobs = [pts_in_hull.astype("float32")]
        self.net.getLayer(self.net.getLayerId("conv8_313_rh")).blobs = [np.full([1, 313], 2.606, "float32")]

        if inputData == "image":
            self.colorizedImage = self.getImageColor()
        if inputData == "video":
            self.getVideoColor()

    # Function to Colorize Image
    def getImageColor(self):
        self.image = cv.imread(self.inputPath)
        return self.processData()
    
    # Function to Colorize Video
    def getVideoColor(self):
        videoCapture = cv.VideoCapture(self.inputPath)

        if not videoCapture.isOpened():
            print("Error capturing video data. Please Try Again.")
            return

        videoCapturing, videoFrame = videoCapture.read()

        with open("settings.json") as file:
            data = json.load(file)
        outputPath = data["outputPath"]

        outputVideo = cv.VideoWriter(path.join(outputPath, path.splitext(path.basename(self.inputPath))[0] + "_colorized.mp4"),
                                     cv.VideoWriter_fourcc(*'mp4v'),
                                     videoCapture.get(cv.CAP_PROP_FPS),
                                     (int(videoCapture.get(cv.CAP_PROP_FRAME_WIDTH)), int(videoCapture.get(cv.CAP_PROP_FRAME_HEIGHT))),
                                    #  isColor=True
                                    )

        print("Colorizing Video...")
        # Print progression bar based on frames processed
        with tqdm(total=int(videoCapture.get(cv.CAP_PROP_FRAME_COUNT))) as progressBar:
            while videoCapturing:
                self.image = videoFrame
                colorizedImage = self.processData()
                outputVideo.write(colorizedImage)
                progressBar.update(1)
                videoCapturing, videoFrame = videoCapture.read()

        videoCapture.release()
        outputVideo.release()
        self.videoOutputPath = path.join(outputPath, path.splitext(path.basename(self.inputPath))[0] + "_colorized.mp4")
        print(f"Colorization Completed! Video saved at: {self.videoOutputPath}")

        return

    # Function to process image colorization by forwarding input images to CNN
    def processData(self):
        self.imageHeight, self.imageWidth = self.image.shape[:2]

        # Normalize the RGB value of the image (between 0-1)
        normalizedImage = self.image.astype("float32") / 255.0
        # Convert Image to LAB color space
        labImage = cv.cvtColor(normalizedImage, cv.COLOR_BGR2LAB)
        # Down Scale Image to fit the CNN model (224 * 224)
        resizedImage = cv.resize(labImage, (224, 224))
        # Extract L channel and subtract 50 for mean-centering
        L, A, B = cv.split(resizedImage) 
        L -= 50

        # Setup input for the CNN model
        self.net.setInput(cv.dnn.blobFromImage(L))
        # Forward the input into the CNN model and obtain the result of A and B channel
        AB_result = self.net.forward()[0, :, :, :].transpose((1, 2, 0))

        # Resize the Image back to its original size
        AB_result = cv.resize(AB_result, (self.imageWidth, self.imageHeight))

        # Obtain original L channel and combine with the AB result
        L, A, B = cv.split(labImage)
        colorizedImage = np.concatenate((L[:, :, np.newaxis], AB_result), axis = 2)

        # Clip the values between 0-1 and Denormalize the values by multiplying 255
        colorizedImage = np.clip(cv.cvtColor(colorizedImage, cv.COLOR_LAB2BGR), 0, 1)
        colorizedImage = (colorizedImage * 255).astype("uint8")

        return colorizedImage

    # Function to compare images before and after colorization
    def compareImage(self):
        colorizedImage = self.colorizedImage
        originalImage = self.image

        if (1920 / (self.imageWidth * 2)) < (1080 / (self.imageHeight * 2)):
            comparisonImage = np.vstack((originalImage, colorizedImage))
            comparisonText = "Colorization Before (Top) and After (Bottom)"
        else:
            comparisonImage = np.hstack((originalImage, colorizedImage))
            comparisonText = "Colorization Before (Left) and After (Right)"
        
        height, width = comparisonImage.shape[:2]
        scalar = min(1920 / width, 1080 / height)
        resizedImage = cv.resize(comparisonImage, (int(width * scalar), int(height * scalar)))
        
        cv.imshow(comparisonText, resizedImage)
        cv.waitKey(0)

    # Function to store images in the output file
    def outputImage(self):
        with open("settings.json") as file:
            data = json.load(file)
        outputPath = data["outputPath"]
        fileName = path.basename(self.inputPath)
        if re.search(".jpg", fileName):
            outputFileName = fileName.replace(".jpg", "_colorized.jpg")
        if re.search(".png", fileName):
            outputFileName = fileName.replace(".png", "_colorized.png")
        cv.imwrite(path.join(outputPath, outputFileName), self.colorizedImage)
        print(f"Image saved at: {outputPath}/{outputFileName}")

    # Function to view video after colorization
    def viewVideo(self):
        videoCapture = cv.VideoCapture(self.videoOutputPath)

        if not videoCapture.isOpened():
            print("Error capturing video data. Please Try Again.")
            return

        videoCapturing, videoFrame = videoCapture.read()
        while videoCapturing:
            cv.imshow("Video Preview", videoFrame)
            if (cv.waitKey(1) & 0xFF) == ord("q"):
                return
            videoCapturing, videoFrame = videoCapture.read()
        videoCapture.release()
        cv.destroyAllWindows()
        return


       
