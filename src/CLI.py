import colorama
import json
import os
import glob
from pathlib import Path
from os import path
from colorama import Fore, Back, Style
from InquirerPy import prompt, get_style, inquirer
from InquirerPy.validator import PathValidator
from numpy import uint8
from .Colorization import *

# Initiate Console Color
colorama.init()

# Declare Default header
header = """
                  ___ __  __    _    ____ _____ 
                 |_ _|  \/  |  / \  / ___| ____|
                  | || |\/| | / _ \| |  _|  _|  
                  | || |  | |/ ___ \ |_| | |___ 
                 |___|_|  |_/_/   \_\____|_____|""" + Fore.LIGHTRED_EX + """
   ____ ___  _     ___  ____  ___ _____   _  _____ ___ ___  _   _ """ + Fore.YELLOW + """
  / ___/ _ \| |   / _ \|  _ \|_ _|__  /  / \|_   _|_ _/ _ \| \ | |""" + Fore.LIGHTYELLOW_EX + """
 | |  | | | | |  | | | | |_) || |  / /  / _ \ | |  | | | | |  \| |""" + Fore.LIGHTGREEN_EX + """
 | |__| |_| | |__| |_| |  _ < | | / /_ / ___ \| |  | | |_| | |\  |""" + Fore.CYAN + """
  \____\___/|_____\___/|_| \_\___/____/_/   \_\_| |___\___/|_| \_|
""" + Style.RESET_ALL

# Declare the CLI questionaire style
style = get_style({
    "questionmark": "#000000",
    "answer": "#61afef",
    "input": "#98c379",
    "question": "#6c85ba",
    "instruction": "",
    "pointer": "#61afef",
    "checkbox": "#98c379",
    "separator": "",
    "skipped": "#5c6370",
    "validator": "",
    "marker": "#e5c07b",
    "fuzzy_prompt": "#c678dd",
    "fuzzy_info": "#98c379",
    "fuzzy_border": "#4b5263",
    "fuzzy_match": "#c678dd",
})

class Interface:
    def __init__(self):
        self.mainMenu()

    # Function to check whether all file paths are loaded
    def loadFilePaths(self):
        try:
            with open("settings.json") as file:
                data = json.load(file)

            invalidPath = []

            for dataPath in data:
                if not path.exists(data[dataPath]):
                    invalidPath.append(f"{dataPath}")

            if len(invalidPath) > 0:
                return {"error": True, "message": invalidPath}
        except Exception as instance:
            return {"error": True, "message": instance}

        return {"error": False, "message": ""}
        
    # Function to show main menu interface
    def mainMenu(self):
        clearConsole = lambda: os.system("cls" if os.name in ("nt", "dos") else "clear")
        clearConsole()
        print(header)
        print("--------------------------------------------------\n")

        totalFileError = 0
        errObj = self.loadFilePaths()
        if errObj["error"]:
            if isinstance(errObj["message"], list):
                print(Fore.RED + "Unable to locate the following file(s) path:")
                for i in errObj["message"]:
                    totalFileError += 1
                    print(i)
                print("Please specify the file(s)' path in the Settings option")
            else:
                print(Fore.RED + "Unexpected Error:")
                print(errObj["message"])
            print(Style.RESET_ALL)
            print("--------------------------------------------------\n")
        
        print("[Main Menu]\n")
        selection = inquirer.select(
            message = "Select an option from the list below:",
            choices = [
                "0. Exit Program",
                "1. Settings",
                "2. Pretrained Image Colorization (.jpg .png)",
                "3. Pretrained Video Colorization (.mp4)"
            ],
            pointer = " ",
            style = style
        ).execute().split(".")[0]
        
        if int(selection) == 0:
            input("Press Enter to Exit the program...")
            return
        if int(selection) == 1:
            self.settings()
            return
        if int(selection) == 2:
            if totalFileError > 0:
                print("Error! Configure the missing files in Settings before proceeding...")
                input("Press Enter to go to Settings...")
                self.settings()
                return
            self.imageColorization()
        
        if int(selection) == 3:
            if totalFileError > 0:
                print("Error! Configure the missing files in Settings before proceeding...")
                input("Press Enter to go to Settings...")
                self.settings()
                return
            self.videoColorization()

    # Function to show settings interface 
    def settings(self):
        clearConsole = lambda: os.system("cls" if os.name in ("nt", "dos") else "clear")
        clearConsole()
        print(header)
        print("--------------------------------------------------\n")

        with open("settings.json") as file:
            data = json.load(file)
        
        print("[Settings]\n")
        selection = inquirer.select(
            message = "Select an option from the list below:",
            choices = [
                "0. Back to Main Menu",
                "1. Edit Caffe Model Path",
                "2. Edit Prototxt Path",
                "3. Edit Cluster Path",
                "4. Edit Image Input Folder Path",
                "5. Edit Image Output Folder Path",
                "6. Show Settings"
            ],
            pointer = " ",
            style = style
        ).execute().split(".")[0]

        if int(selection) == 0:
            self.mainMenu()
            return
        
        if int(selection) == 1:
            modelpath = inquirer.filepath(
                message = "Enter path to the .caffemodel file:",
                validate=PathValidator(is_file = True, message="Input is not a file"),
                style = style
            ).execute()
            data["modelPath"] = modelpath
            with open("settings.json", "w") as outputfile:
                json.dump(data, outputfile)         
            self.settings()
            return

        if int(selection) == 2:
            prototxtPath = inquirer.filepath(
                message = "Enter path to the .prototxt file:",
                validate=PathValidator(is_file = True, message="Input is not a file"),
                style = style
            ).execute()
            data["prototxtPath"] = prototxtPath
            with open("settings.json", "w") as outputfile:
                json.dump(data, outputfile)         
            self.settings()
            return

        if int(selection) == 3:
            clusterPath = inquirer.filepath(
                message = "Enter path to the Cluster (.npy) file:",
                validate=PathValidator(is_file = True, message="Input is not a file"),
                style = style
            ).execute()
            data["clusterPath"] = clusterPath
            with open("settings.json", "w") as outputfile:
                json.dump(data, outputfile)         
            self.settings()
            return

        if int(selection) == 4:
            inputPath = inquirer.filepath(
                message = "Enter folder path to the Input Image directory:",
                validate=PathValidator(is_dir = True, message="Input is not a directory"),
                style = style
            ).execute()
            data["inputPath"] = inputPath
            with open("settings.json", "w") as outputfile:
                json.dump(data, outputfile)         
            self.settings()
            return

        if int(selection) == 5:
            outputPath = inquirer.filepath(
                message = "Enter folder path to the Output Image directory:",
                validate=PathValidator(is_dir = True, message="Input is not a directory"),
                style = style
            ).execute()
            data["outputPath"] = outputPath
            with open("settings.json", "w") as outputfile:
                json.dump(data, outputfile)         
            self.settings()
            return

        if int(selection) == 6:
            for i in data:
                print(f"{i}\t: {data[i]}")
            input("Press Enter to go back to Settings...")
            self.settings()
            return

    # Function to show image colorization interface 
    def imageColorization(self):
        clearConsole = lambda: os.system("cls" if os.name in ("nt", "dos") else "clear")
        clearConsole()
        print(header)
        print("--------------------------------------------------\n")

        with open("settings.json") as file:
            data = json.load(file)

        print("[Pretrained Image Colorization]\n")
        selection = inquirer.select(
            message = "Select an option from the list below:",
            choices = [
                "0. Back to Main Menu",
                "1. Custom Input Image Path",
                "2. Select Image(s) from Input Folder",
            ],
            pointer = " ",
            style = style
        ).execute().split(".")[0]

        if int(selection) == 0:
            self.mainMenu()
            return

        if int(selection) == 1:
            imagePath = inquirer.filepath(
                message = "Enter path to the Image file:",
                validate=PathValidator(is_file = True, message="Input is not a file"),
                style = style
            ).execute()

            inst = Colorization(imagePath, inputData = "image")
            inst.outputImage()
            self.imageColorizationFunc(inst)
            
            return
        
        if int(selection) == 2:
            imgdir = data["inputPath"]
            imgext = ["jpg", "png"]
            imagesPath = []
            [imagesPath.extend(glob.iglob(imgdir + "**/*." + e)) for e in imgext]
            
            imageOptions = ["RETURN"]
            for images in imagesPath:
                imageOptions.append({
                    "name": path.basename(images),
                    "value": images
                })

            imageToColorize = inquirer.select(
            message = "Select an option from the list below:",
            choices = imageOptions,
            pointer = " ",
            style = style
            ).execute()

            if imageToColorize == "RETURN":
                self.imageColorization()
                return

            inst = Colorization(imageToColorize, inputData = "image")
            inst.outputImage()
            self.imageColorizationFunc(inst)

            return

    # Function to show video colorization interface 
    def videoColorization(self):
        clearConsole = lambda: os.system("cls" if os.name in ("nt", "dos") else "clear")
        clearConsole()
        print(header)
        print("--------------------------------------------------\n")

        with open("settings.json") as file:
            data = json.load(file)

        print("[Pretrained Video Colorization]\n")
        selection = inquirer.select(
            message = "Select an option from the list below:",
            choices = [
                "0. Back to Main Menu",
                "1. Custom Input Video Path",
                "2. Select Video(s) from Input Folder",
            ],
            pointer = " ",
            style = style
        ).execute().split(".")[0]

        if int(selection) == 0:
            self.mainMenu()
            return

        if int(selection) == 1:
            while True:
                videoPath = inquirer.filepath(
                    message = "Enter path to the Video file:",
                    validate=PathValidator(is_file = True, message="Input is not a file"),
                    style = style
                ).execute()

                name, extension = path.splitext(videoPath)
                if extension != ".mp4":
                    print("Input is not a .mp4 file")
                else:
                    break

            inst = Colorization(videoPath, inputData = "video")
            self.videoColorizationFunc(inst)
            
            return

        if int(selection) == 2:
            viddir = data["inputPath"]
            videosPath = []

            videosPath.extend(glob.iglob(viddir + "**/*.mp4"))
            
            videoOptions = ["RETURN"]
            for videos in videosPath:
                videoOptions.append({
                    "name": path.basename(videos),
                    "value": videos
                })

            videoToColorize = inquirer.select(
            message = "Select an option from the list below:",
            choices = videoOptions,
            pointer = " ",
            style = style
            ).execute()

            if videoToColorize == "RETURN":
                self.videoColorization()
                return

            inst = Colorization(videoToColorize, inputData = "video")
            self.videoColorizationFunc(inst)

            return
    
    # Function to show additional image colorization functionalities interface 
    def imageColorizationFunc(self, instance):
        selection = inquirer.select(
            message = "Select an option from the list below:",
            choices = [
                "0. Back to Main Menu",
                "1. Compare Original & Colorized Image",
                "2. Colorize Another Image",
            ],
            pointer = " ",
            style = style
        ).execute().split(".")[0]

        if int(selection) == 0:
            self.mainMenu()
            return

        if int(selection) == 1:
            instance.compareImage()
            input("Press Enter to return to previous page...")
            self.imageColorizationFunc(instance)
            return

        if int(selection) == 2:
            self.imageColorization()
            return

    # Function to show additional video colorization functionalities interface 
    def videoColorizationFunc(self, instance):
        selection = inquirer.select(
            message = "Select an option from the list below:",
            choices = [
                "0. Back to Main Menu",
                "1. View Colorized Video",
                "2. Colorize Another Video",
            ],
            pointer = " ",
            style = style
        ).execute().split(".")[0]

        if int(selection) == 0:
            self.mainMenu()
            return

        if int(selection) == 1:
            instance.viewVideo()
            input("Press Enter to return to previous page...")
            self.videoColorizationFunc(instance)
            return

        if int(selection) == 2:
            self.videoColorization()
            return