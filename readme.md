Generates Image + Corresponding Joint Position Data

### Instructions for Image/Joint Generation
#### Blender Configuration -- /blender-scripts/
1. Download Blender 2.79b
2. Edit config-blender.py data_out to directory location for output data
2. Edit config-blender.py dir_mhx2 to directory location of input makeHumans (git link)
2. Edit config-blender.py dir_bvhposes to directory location of input singleframe bvh mocap poses (git link)
3. Edit blender_dir in 'run-blender.py' and 'core-blender.py'
#### Execute run.py

## Image Creation Parameters

-   Random Makehuman Figure (repo)
-   Random .bvh Single Pose (repo)
-   Scale down to Fit in Frame
-   Random Rotation (z in range(360deg)) (x in range(TBDdeg)) (y in range(TBDdeg)) - From Side View Camera
-   Double Lamp Light In Coordinates (TBD)

# JointLocations

##Two Root Locations, Pelvis and Head (For Normalization)

##Joint Heirarchy - Corresponding to Rows of Output CSV from generate-blender.py

###All joint coords. Absolute

pelvis: relative to camera ------TBD!!!------  
-lowerBack  
--midBack  
---spine  
----topSpine  
-----neck  
------head: relative to camera ------TBD!!!------  
-------crown  
-----scLeft: 'rel-topSpine'  
------leftShoulder  
-------leftElbow  
--------leftWrist  
---------leftHand  
----------leftThumbBase  
-----------leftThumb  
----------leftFingerBase  
-----------leftFinger   
-----scRight: 'rel-topSpine'  
------rightShoulder  
-------rightElbow  
--------rightWrist  
---------rightHand  
----------rightThumbBase  
-----------rightThumb  
----------rightFingerBase  
-----------rightFinger  
-leftHip: 'rel-pelvis'  
--leftKnee  
---leftAnkle  
----leftFoot  
-----leftToe  
-rightHip: 'rel-pelvis'  
--rightKnee  
---rightAnkle  
----rightFoot  
-----rightToe  
 