"""
Functions for Blender Image/JointPosition Creation
"""

# Lib Directory
blender_dir = (
    "/Users/warrentaylor/Desktop/movement/synthetic-makehuman/blender-posed-images/blender-scripts"
)

import bpy
import bpy_extras
import numpy as np
from collections import OrderedDict

# Import Lib
import imp

configBlender = imp.load_source("configBlender", (blender_dir + "/config-blender.py"))

def delete(objects):
    """
    Delete Objects for Next Iteration
    :param objects: Either 'All' or 'humans' or 'lamps' or 'cameras'
    :return:
    """
    if objects == "All":
        bpy.ops.object.select_all()
        bpy.ops.object.select_all()
        bpy.ops.object.delete()
        return
    else:
        raise Exception("Unavaliable Object Deletion Parameter")


def lampCreate(type, location, rotation):
    """
    Create Lamp with Determined Location and Rotation
    :param type: type of lamp 'SUN' or 'POINT'
    :param location: 3-vec (x,y,z)
    :param rotation: 3-vec (rx,ry,rz)
    :return:
    """
    bpy.ops.object.lamp_add(
        type=type, view_align=False, location=location, rotation=rotation
    )
    return


def cameraCreate(location, rotation):
    """
    Create Camera with Determined Location and Rotation
    :param location: 3-vec (x,y,z)
    :param rotation: 3-vec (rx,ry,rz)
    :return:
    """
    bpy.ops.object.camera_add(location=location, rotation=rotation)
    return


def loadSubject(makeHuman, bvhFrame):
    """
    Load and Target makeHuman + bvh Frame
    :param makeHuman: Full Filepath to makeHuman
    :param bvhFrame:  Full Filepath to .bvh single frame
    :return:
    """
    # import makeHuman subject
    bpy.ops.import_scene.makehuman_mhx2(filepath=makeHuman)
    # load .bvh video frame
    bpy.ops.mcp.load_and_retarget(filepath=bvhFrame)
    # go to first video frame (0th is T-pose)
    bpy.context.scene.frame_set(1)
    ################### delete T-pose frame in Dopesheet_editor
    ##########################bpy.context.area.type = "DOPESHEET_EDITOR"
    ##############################bpy.ops.action.delete()                        DELETE
    ##############################bpy.context.area.type = "TEXT_EDITOR"
    return


def centerSubject(scaleFactor, rotationFactor):
    """
    Center and Rotate Subject about Origin
    :param scaleFactor: 3-vector of x,y,z scaling factors
    :param rotationFactor: 3-vector of x,y,z rotation factors in radians
    :return:
    """
    # set object to center (clear translations)
    bpy.ops.pose.loc_clear()
    # change to object mode
    bpy.ops.object.mode_set(mode="OBJECT")
    # scale object (need to scale x,y,z)
    bpy.data.objects["1"].scale = scaleFactor
    # rotate object in x,y,z
    bpy.data.objects["1"].rotation_euler = rotationFactor
    return


def renderImage(resolution, file_extension, dir, i):
    """
    Render Image at Current Camera Config to Disk
    :param res_x: Resolution in x
    :param res_y: Resolution in y
    :param file_extension: File extension type for export
    :param dir: Directory to Export Img
    :param i: i'th image for export filename
    :return:
    """
    # ---------- RENDER IMAGE ----------#
    # render resolution
    bpy.context.scene.render.resolution_x = resolution
    bpy.context.scene.render.resolution_y = resolution
    bpy.data.scenes["Scene"].render.resolution_percentage = 100
    # image settings
    bpy.context.scene.render.image_settings.color_mode = "RGB"
    bpy.context.scene.render.image_settings.file_format = file_extension
    ######################################### disable metadata                                       DELETE THIS
    ##########################################3#bpy.data.scenes["Scene"].render.use_stamp_time
    #################################################bpy.data.scenes["Scene"].render.use_stamp_date
    ###############################bpy.data.scenes["Scene"].render.use_stamp_render_time
    ############################3bpy.data.scenes["Scene"].render.use_stamp_frame
    ##########################3#bpy.data.scenes["Scene"].render.use_stamp_scene
    ##########################bpy.data.scenes["Scene"].render.use_stamp_camera
    ##############################bpy.data.scenes["Scene"].render.use_stamp_filename
    # file name (will automatically add .jpg)
    bpy.context.scene.render.filepath = dir + "/" + str(i)
    # set start/end animation to frame 2
    bpy.data.scenes["Scene"].frame_start = 2
    bpy.data.scenes["Scene"].frame_end = 2
    # render image
    bpy.ops.render.render(write_still=True)
    return


def bonePixelCoords(bone_name, which_end, depth_zero):
    # Convert to Pixel Coordinates (Bottom Left is 0,0 - Top Right is 1,1 - Depth is Positive)

    # If armature not at zero, break loop
    armature = "1"
    if np.sum(bpy.data.objects[armature].location) != 0:
        raise Exception("Error: Posed Model Not Centered")

    # Necessary Parameters for Camera Coordinates
    context = bpy.context
    scene = context.scene
    # Set camera = current camera object
    camera = bpy.data.objects["Camera"]

    # Get World Coordinates of Joint, Both the Correct End of Bone and the Opposite
    if which_end == "head":
        wco = bpy.data.objects[armature].pose.bones[bone_name].head
    elif which_end == "tail":
        wco = bpy.data.objects[armature].pose.bones[bone_name].tail
    else:
        raise Exception("Unknown Bone End: {}".format(which_end))

    # Convert World Coordinates to Camera Coordinates
    cco = bpy_extras.object_utils.world_to_camera_view(scene, camera, wco)
    print("World Coordinates for {} : {}".format(bone_name, wco))
    print("Camera Coordinates for {} : {}".format(bone_name,cco))

    output_joint = np.zeros(3)
    output_joint[0] = round(cco[0] * configBlender.resolution, configBlender.coordinates_SigFig)
    output_joint[1] = round(cco[1] * configBlender.resolution, configBlender.coordinates_SigFig)
    # Convert Depth to Pixel Coordinates
    output_joint[2] = round((cco[2]-depth_zero), configBlender.coordinates_SigFig)

    return output_joint


def findJointCoordinates():
    """
    Find Joint Coordinates in Camera Reference Frame
    :return:
    """
    # If armature not at zero, break loop
    armature = "1"
    if np.sum(bpy.data.objects[armature].location) != 0:
        raise Exception("Error: Posed Model Not Centered")

    # Coordinates String for json write
    coordinates = ["x", "y", "z"]
    # Necessary Parameters for Camera Coordinates
    context = bpy.context
    scene = context.scene
    # Set camera = current camera object
    camera = bpy.data.objects["Camera"]

    # Root Pelvis Zero-Depth
    wco_pelvis = bpy.data.objects[armature].pose.bones["Hips"].head
    cco_pelvis = bpy_extras.object_utils.world_to_camera_view(scene, camera, wco_pelvis)
    depth_zero = cco_pelvis[2]





    # Find Pixel Joint Coordinates

    pelvis_pix = bonePixelCoords("Hips", "head", depth_zero)
    print(pelvis_pix)
    leftFoot_pix = bonePixelCoords("LeftFoot", "tail", depth_zero)
    print(leftFoot_pix)





    # Convert Pixel Joint Coordinates to json
    joints = OrderedDict(
        [
            (
                "Pelvis",
                OrderedDict(
                    [("Coordinates", OrderedDict(zip(coordinates, pelvis_pix)))]
                ),
            )
        ]
    )
    # Set Pelvis Root to 0
    joints["Pelvis"]["Coordinates"]["z"] = 0
    print(joints)

    ###Spine/Head
    pelvis = bpy.data.objects[armature].pose.bones["Hips"].head
    lowerBack = bpy.data.objects[armature].pose.bones["Hips"].tail
    midBack = bpy.data.objects[armature].pose.bones["LowerBack"].tail
    spine = bpy.data.objects[armature].pose.bones["Spine"].tail
    topSpine = bpy.data.objects[armature].pose.bones["Spine1"].tail
    neck = bpy.data.objects[armature].pose.bones["Neck"].tail
    head = bpy.data.objects[armature].pose.bones["Neck1"].tail
    crown = bpy.data.objects[armature].pose.bones["Head"].tail
    ###Left Arm
    scLeft = bpy.data.objects[armature].pose.bones["LeftShoulder"].head
    leftShoulder = bpy.data.objects[armature].pose.bones["LeftShoulder"].tail
    leftElbow = bpy.data.objects[armature].pose.bones["LeftArm"].tail
    leftWrist = bpy.data.objects[armature].pose.bones["LeftForeArm"].tail
    leftHand = bpy.data.objects[armature].pose.bones["LeftHand"].tail
    leftThumbBase = bpy.data.objects[armature].pose.bones["LThumb"].head
    leftThumb = bpy.data.objects[armature].pose.bones["LThumb"].tail
    leftFingerBase = bpy.data.objects[armature].pose.bones["LeftFingerBase"].tail
    leftFinger = bpy.data.objects[armature].pose.bones["LeftHandFinger1"].tail
    ###Right Arm
    scRight = bpy.data.objects[armature].pose.bones["RightShoulder"].head
    rightShoulder = bpy.data.objects[armature].pose.bones["RightShoulder"].tail
    rightElbow = bpy.data.objects[armature].pose.bones["RightArm"].tail
    rightWrist = bpy.data.objects[armature].pose.bones["RightForeArm"].tail
    rightHand = bpy.data.objects[armature].pose.bones["RightHand"].tail
    rightThumbBase = bpy.data.objects[armature].pose.bones["RThumb"].head
    rightThumb = bpy.data.objects[armature].pose.bones["RThumb"].tail
    rightFingerBase = bpy.data.objects[armature].pose.bones["RightFingerBase"].tail
    rightFinger = bpy.data.objects[armature].pose.bones["RightHandFinger1"].tail
    ###Left Leg
    leftHip = bpy.data.objects[armature].pose.bones["LHipJoint"].tail
    leftKnee = bpy.data.objects[armature].pose.bones["LeftUpLeg"].tail
    leftAnkle = bpy.data.objects[armature].pose.bones["LeftLeg"].tail
    leftFoot = bpy.data.objects[armature].pose.bones["LeftFoot"].tail
    leftToe = bpy.data.objects[armature].pose.bones["LeftToeBase"].tail
    ###Right Leg
    rightHip = bpy.data.objects[armature].pose.bones["RHipJoint"].tail
    rightKnee = bpy.data.objects[armature].pose.bones["RightUpLeg"].tail
    rightAnkle = bpy.data.objects[armature].pose.bones["RightLeg"].tail
    rightFoot = bpy.data.objects[armature].pose.bones["RightFoot"].tail
    rightToe = bpy.data.objects[armature].pose.bones["RightToeBase"].tail

    return joints
