# image-colorization-python
This Project is developed for academic and research purposes.

## Default File Structure
```
├─ /input
├─ /model
  ├─ .prototxt file
  ├─ .caffemodel file
  └─ .npy file
├─ /output
└─ settings.json
```

## How to run?
1. Install the [requirements](https://github.com/JYKM/image-colorization-python#requirements) and [dependencies](https://github.com/JYKM/image-colorization-python#dependencies)
2. Run **main.py** file

## Requirements
Python 3.1+ (Preferably Python 3.9.5 or above), the dependencies and the following files

Store the following 3 files in a folder and locate them in the program (settings.json)

[Caffe Model Link](http://eecs.berkeley.edu/~rich.zhang/projects/2016_colorization/files/demo_v2/colorization_release_v2.caffemodel)

[Prototxt Link](https://github.com/richzhang/colorization/blob/caffe/models/colorization_deploy_v2.prototxt)

[Cluster Center Link](https://github.com/richzhang/colorization/blob/caffe/resources/pts_in_hull.npy)

## Dependencies
pip install -r requirements.txt

## Citation
For further reading: http://richzhang.github.io/colorization/ 
```
@inproceedings{zhang2016colorful,
  title={Colorful Image Colorization},
  author={Zhang, Richard and Isola, Phillip and Efros, Alexei A},
  booktitle={ECCV},
  year={2016}
}
```
