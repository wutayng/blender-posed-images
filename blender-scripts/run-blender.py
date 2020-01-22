"""
Using Blender-v2.79b
"""

# Lib Directory
blender_dir = "/Users/warrentaylor/Desktop/movement/synthetic-makehuman/blender-posed-images/blender-scripts"

import os
import bpy
import json

# Import Lib/Core
import imp

configBlender = imp.load_source("configBlender", (blender_dir + "/config-blender.py"))
coreBlender = imp.load_source("coreBlender", (blender_dir + "/core-blender.py"))


# Create Output Image Folder
try:
    os.mkdir(configBlender.data_out)
except:
    pass

# Delete All Objects Before Starting
coreBlender.delete("All")

for i in range(1, 2):

    # Load Subject & .bvh Frame
    makeHuman = configBlender.dir_mhx2 + "1/1/1.mhx2"
    bvhFrame = configBlender.dir_bvhposes + str(i) + "/10/10.bvh"
    coreBlender.loadSubject(makeHuman, bvhFrame)

    # Center Subject, Scale, and Rotate about Origin
    coreBlender.centerSubject(
        configBlender.mh_scaleFactor, configBlender.mh_rotationFactor
    )

    # Necessary Parameters
    context = bpy.context
    scene = context.scene
    # Create Camera
    coreBlender.cameraCreate((15, 0, 4), (1.5708, 0, 1.5708))
    # Render Camera Parameters
    scene.camera = context.object
    # Create Lamp
    coreBlender.lampCreate("POINT", (5, 0, 5), (0.0, 0.0, 0.0))

    # Render Image to Output File
    coreBlender.renderImage(configBlender.resolution, "JPEG", configBlender.data_out, i)

    # Find all Joint Coordinates in Pixel Dimensions
    joints = coreBlender.findJointCoordinates()

    # write each joint to file
    # f = open(jointsout + str(i) + ".csv", "w")
    # f.write("%10.6f, %10.6f, %10.6f\n" % (pelvis[0], pelvis[1], pelvis[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (lowerBack[0], lowerBack[1], lowerBack[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (midBack[0], midBack[1], midBack[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (spine[0], spine[1], spine[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (topSpine[0], topSpine[1], topSpine[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (neck[0], neck[1], neck[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (head[0], head[1], head[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (crown[0], crown[1], crown[2]))
    ## ---
    # f.write("%10.6f, %10.6f, %10.6f\n" % (scLeft[0], scLeft[1], scLeft[2]))
    # f.write(
    #    "%10.6f, %10.6f, %10.6f\n" % (leftShoulder[0], leftShoulder[1], leftShoulder[2])
    # )
    # f.write("%10.6f, %10.6f, %10.6f\n" % (leftElbow[0], leftElbow[1], leftElbow[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (leftWrist[0], leftWrist[1], leftWrist[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (leftHand[0], leftHand[1], leftHand[2]))
    # f.write(
    #    "%10.6f, %10.6f, %10.6f\n"
    #    % (leftThumbBase[0], leftThumbBase[1], leftThumbBase[2])
    # )
    # f.write("%10.6f, %10.6f, %10.6f\n" % (leftThumb[0], leftThumb[1], leftThumb[2]))
    # f.write(
    #    "%10.6f, %10.6f, %10.6f\n"
    #    % (leftFingerBase[0], leftFingerBase[1], leftFingerBase[2])
    # )
    # f.write("%10.6f, %10.6f, %10.6f\n" % (leftFinger[0], leftFinger[1], leftFinger[2]))
    ## ---
    # f.write("%10.6f, %10.6f, %10.6f\n" % (scRight[0], scRight[1], scRight[2]))
    # f.write(
    #    "%10.6f, %10.6f, %10.6f\n"
    #    % (rightShoulder[0], rightShoulder[1], rightShoulder[2])
    # )
    # f.write("%10.6f, %10.6f, %10.6f\n" % (rightElbow[0], rightElbow[1], rightElbow[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (rightWrist[0], rightWrist[1], rightWrist[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (rightHand[0], rightHand[1], rightHand[2]))
    # f.write(
    #    "%10.6f, %10.6f, %10.6f\n"
    #    % (rightThumbBase[0], rightThumbBase[1], rightThumbBase[2])
    # )
    # f.write("%10.6f, %10.6f, %10.6f\n" % (rightThumb[0], rightThumb[1], rightThumb[2]))
    # f.write(
    #    "%10.6f, %10.6f, %10.6f\n"
    #    % (rightFingerBase[0], rightFingerBase[1], rightFingerBase[2])
    # )
    # f.write(
    #    "%10.6f, %10.6f, %10.6f\n" % (rightFinger[0], rightFinger[1], rightFinger[2])
    # )
    ## ---
    # f.write("%10.6f, %10.6f, %10.6f\n" % (leftHip[0], leftHip[1], leftHip[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (leftKnee[0], leftKnee[1], leftKnee[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (leftAnkle[0], leftAnkle[1], leftAnkle[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (leftFoot[0], leftFoot[1], leftFoot[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (leftToe[0], leftToe[1], leftToe[2]))
    ## ---
    # f.write("%10.6f, %10.6f, %10.6f\n" % (rightHip[0], rightHip[1], rightHip[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (rightKnee[0], rightKnee[1], rightKnee[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (rightAnkle[0], rightAnkle[1], rightAnkle[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (rightFoot[0], rightFoot[1], rightFoot[2]))
    # f.write("%10.6f, %10.6f, %10.6f\n" % (rightToe[0], rightToe[1], rightToe[2]))

    # Write Joint Dict to Json File
    with open(configBlender.data_out + "/result.json", "w") as fp:
        json.dump(joints, fp)

    # Delete Everything for Next Iteration
    coreBlender.delete("All")

    i += 1

