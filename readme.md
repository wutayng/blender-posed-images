# To Generate Human Posed Image + Corresponding Joint Position Data

## Installation/Config
### Blender
* Download blender   
* Download import_runtime_mhx2 and MakeWalk add-ons - open blender and enable both  
* Add-ons above must be compatible with blender version  
### Github
* Clone Repo
* Create venv
```
pip install requirements.txt
```
- Edit directory locations in config.py (4 path locations) and blender.py (1 data_out location)  
## Execution
### Test
Test to Display a Sample output image with joint coordinates shown + 3D Joints Matplotlib Plot  
- Blender will open in this script: you can analyze then close to view the plots above
```
$ python3 run.py test
```
### Collect Data
Outputs images with joint coordinates shown + 3D Joints .csv In Image Pixel Perspective Coordinates  
#### For instructions on how to Convert Image Perspective Joint .csv to Global, see:   
#### - Google Drive/Technical Resources/Perspective Coordinate Transformation  
- Set config.py iterations_total  
- Total Output Image/.csv Number will be iterations_total * 10
```
$ python3 run.py data
```

## Image Creation Parameters

-   Random Makehuman Figure (repo)
-   Random .bvh Single Pose (repo)
-   Random Rotation, Lighting
-   Image Resolution + Other Camera Parameters. in config.py

## JointLocations

### Output Joints .csv is In Image Pixel Coordinates w/ Perspective

### Joint Heirarchy - Corresponding to Rows of Output CSV from generate-blender.py
```

└── pelvis  
    ├── lowerBack  
    │   └── midBack  
    │       └── spine  
    │           └── topSpine  
    │               ├── neck  
    │               │   └── head  
    │               │   │   └── crown  
    │               ├── scLeft  
    │               │   └── leftShoulder  
    │               │       └── leftElbow  
    │               │           └── leftWrist  
    │               │               └── leftHand  
    │               │                   ├── leftThumbBase  
    │               │                   │   └── leftThumb  
    │               │                   └── leftFingerBase  
    │               │	                    └── leftFinger   
    │               └── scRight  
    │                   └── rightShoulder  
    │                       └── rightElbow  
    │                           └── rightWrist  
    │				    └── rightHand  
    │                               	├── rightThumbBase  
    │                                   │   └── rightThumb  
    │                                   └── rightFingerBase  
    │                                       └── rightFinger  
    ├── leftHip  
    │   └── leftKnee  
    │       └── leftAnkle  
    │           └── leftFoot  
    │               └── leftToe  
    └── rightHip  
        └── rightKnee   
            └── rightAnkle   
                └── rightFoot   
                    └── rightToe   
```

## Attributions

[Blender](https://www.blender.org/)
 
