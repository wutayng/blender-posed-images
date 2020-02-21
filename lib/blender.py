"""
Import mhx2, random .bvh singleframe pose, random camera parameters, random lighting
"""
data_out = "/home/warren/data/synthetic-training/blender-data"

# Image Render Size
resolution = 1000

# Coordinates Round() Parameter - Significant Figures
coordinates_SigFig = 3

import bpy, csv, os, bpy_extras, mathutils, random
import numpy as np
from bpy import context


# Bounding Box Class for Camera Placement
class boundingBox:
    def __init__(self):
        # Initialize Min[0] / Max[1] Values
        # Make Arbitrarily High so they are fit by Character Pose
        self.x = [100, -100]
        self.y = [100, -100]
        self.z = [100, -100]


# Joint Coordinates
class Joint:
    def __init__(self, name, bone, end):
        self.name = name
        self.bone = bone
        self.end = end
        self.gcs = None
        self.pcs = None

    def get_gcs(self, armature):
        """
        Get Global Coordinates of Joint
        :param armature: String name of the mhx2 Character in Blender
        :return:
        """
        if self.end == "head":
            self.gcs = bpy.data.objects[armature].pose.bones[self.bone].head
        elif self.end == "tail":
            self.gcs = bpy.data.objects[armature].pose.bones[self.bone].tail
        else:
            raise Exception("Joint {} does not have Head or Tail".format(self.name))

    def get_pcs(self, scene, camera, resolution, armature):
        """
        Get Pixel Coordinates of Joint
        :param scene: Blender Scene - found by: context = bpy.context, scene = context.scene
        :param camera: Blender Current Camera - found by: camera = bpy.data.objects["Camera"]
        :param resolution: XY resolution of square image
        :param armature: String name of the mhx2 Character in Blender
        :return:
        """
        if self.gcs is None:
            raise Exception(
                "Joint {} needs global coordinates before pixel coordinates can be found".format(
                    self.name
                )
            )

        else:
            ccs = bpy_extras.object_utils.world_to_camera_view(scene, camera, self.gcs)
            self.pcs = ccs * resolution
            # Scale Back Z Depth Coordinate
            self.pcs[2] = self.pcs[2] / resolution


jointsTitlesList = [
    # Name - Bone Name - End Name - Named Dependencies List
    ["pelvis", "Hips", "head"],
    ["lower_back", "Hips", "tail"],
    ["mid_back", "LowerBack", "tail"],
    ["spine", "Spine", "tail"],
    ["neck", "Spine1", "tail"],
    ["upper_neck", "Neck", "tail"],
    ["head", "Neck1", "tail"],
    ["crown", "Head", "tail"],
    ["sc_left", "LeftShoulder", "head"],
    ["shoulder_left", "LeftShoulder", "tail"],
    ["elbow_left", "LeftArm", "tail"],
    ["wrist_left", "LeftForeArm", "tail"],
    ["hand_left", "LeftHand", "tail"],
    ["thumb_base_left", "LThumb", "head"],
    ["thumb_left", "LThumb", "tail"],
    ["finger_base_left", "LeftFingerBase", "tail"],
    ["finger_left", "LeftHandFinger1", "tail"],
    ["hip_left", "LHipJoint", "tail"],
    ["knee_left", "LeftUpLeg", "tail"],
    ["ankle_left", "LeftLeg", "tail"],
    ["foot_left", "LeftFoot", "tail"],
    ["toe_left", "LeftToeBase", "tail"],
    ["sc_right", "RightShoulder", "head"],
    ["shoulder_right", "RightShoulder", "tail"],
    ["elbow_right", "RightArm", "tail"],
    ["wrist_right", "RightForeArm", "tail"],
    ["hand_right", "RightHand", "tail"],
    ["thumb_base_right", "RThumb", "head"],
    ["thumb_right", "RThumb", "tail"],
    ["finger_base_right", "RightFingerBase", "tail"],
    ["finger_right", "RightHandFinger1", "tail"],
    ["hip_right", "RHipJoint", "tail"],
    ["knee_right", "RightUpLeg", "tail"],
    ["ankle_right", "RightLeg", "tail"],
    ["foot_right", "RightFoot", "tail"],
    ["toe_right", "RightToeBase", "tail"],
]


def delete(objects):
    """
    Delete Objects for Next Iteration
    :param objects: Either 'All' or 'lamps/cameras'
    :return:
    """
    if objects == "All":
        bpy.ops.object.select_all()
        bpy.ops.object.select_all()
        bpy.ops.object.delete()
        return
    else:
        raise Exception("Unavailable Object Deletion Parameter")


def equipRandomPose():
    """
    Equip Pose and Move to Frame 1 (Frame 0 is T Pose)
    :return:
    """
    bpy.ops.mcp.load_and_retarget(filepath=str(data_out + "/temp/temp_bvh_pose.bvh"))
    # go to first video frame (0th is T-pose)
    bpy.context.scene.frame_set(1)
    return


def rotateObject(obj, angle, direction_str, point):
    """
    Rotate Object Around a certain Point
    :param obj: Blender Object
    :param angle: Angle in Radians of How Far to Rotate
    :param direction_str: 'X' 'Y' or 'Z'
    :param point: Point of Rotation (3-vector)
    :return:
    """
    r_mat = mathutils.Matrix.Rotation(angle, 4, direction_str)
    t_mat = mathutils.Matrix.Translation(point)
    m_mat = t_mat * r_mat * t_mat.inverted()
    obj.location = m_mat * obj.location
    obj.rotation_euler.rotate(m_mat)
    return


def createCamera(jointsList, camera_yaw):
    """
    Create Random Camera Position in View of Posed Chararcter
    :param jointsList: List of Joint Objects to Form Global Bounding Box
    :param camera_yaw: z_yaw, the rotation of camera horizontally around the subject (important for lighting)
    """
    # Find Pose Bounding Box
    bbox = boundingBox()
    for elem in jointsList:
        # X LIM
        if elem.gcs[0] < bbox.x[0]:
            bbox.x[0] = elem.gcs[0]
        if elem.gcs[0] > bbox.x[1]:
            bbox.x[1] = elem.gcs[0]
        # Y LIM
        if elem.gcs[1] < bbox.y[0]:
            bbox.y[0] = elem.gcs[1]
        if elem.gcs[1] > bbox.y[1]:
            bbox.y[1] = elem.gcs[1]
        # Z LIM
        if elem.gcs[2] < bbox.z[0]:
            bbox.z[0] = elem.gcs[2]
        if elem.gcs[2] > bbox.z[1]:
            bbox.z[1] = elem.gcs[2]

    # Find bounding box center in global coordinates
    bbox_center = np.array([sum(bbox.x) / 2, sum(bbox.y) / 2, sum(bbox.z) / 2])
    # Find Euclidean Distance to Bounding Box Corner
    bbox_radius = np.sqrt(
        (bbox.x[1] - bbox_center[0]) ** 2
        + (bbox.y[1] - bbox_center[1]) ** 2
        + (bbox.z[1] - bbox_center[2]) ** 2
    )
    # Create Horizontal Camera in Bounding Box Middle With Character in View
    camera_fov = np.pi / 4
    # 10% Buffer Distance
    bpy.ops.object.camera_add(
        location=(
            bbox_center[0] + ((bbox_radius / (np.tan(camera_fov / 2))) * 1.1),
            bbox_center[1],
            bbox_center[2],
        ),
        rotation=(1.5708, 0, 1.5708),
    )
    # Random Rotation of Camera
    cam_obj = bpy.data.objects["Camera"]
    x_roll = np.random.normal(
        0, 0.01
    )  # X Rotation is ROLL About Axis Coming Out of the Camera
    y_pitch = np.random.normal(
        -np.pi / 8, np.pi / 8
    )  # Y Rotation is PITCH About Horizon Line Axis, Fall Forwards or Backwards
    z_yaw = camera_yaw  # Z Rotation is YAW About Z-Axis Perpendicular to Ground Surface
    rotateObject(cam_obj, x_roll, "X", bbox_center)
    rotateObject(cam_obj, y_pitch, "Y", bbox_center)
    rotateObject(cam_obj, z_yaw, "Z", bbox_center)
    # Lengthen Camera Clipping
    bpy.data.cameras["Camera"].clip_end = 1000
    # Scene Params
    scene = context.scene
    scene.camera = context.object
    return


def createRandomLamp(type, mhx2_name, camera_yaw):
    """
    Create Lamp with Determined Location and Rotation
    :param type: type of lamp 'SUN' or 'POINT'
    :param mhx2_name: for location consideration (point only)
    :param camera_yaw: align sun directionality w/ camera view (sun only)
    :return:
    """
    if type == "SUN":
        vert_rot = random.triangular(
            0, 3.14159, 0.7854
        )  # Mode of Choice is 45deg Sun Pointing Down
        # Horizontal Limits from Left to Right of Subject
        horz_rot = camera_yaw + (np.pi / 2) + random.uniform(-np.pi / 2, np.pi / 2)
        location = (0, 0, 0)
        rotation = (vert_rot, 0, horz_rot)
        bpy.ops.object.lamp_add(
            type=type, view_align=False, location=location, rotation=rotation
        )
    elif type == "POINT":
        character_root = bpy.data.objects[mhx2_name].pose.bones["Hips"].tail
        radius = 15  # Max Distance Away From Character
        x_loc = character_root[0] + random.uniform(-radius, radius)
        y_loc = character_root[1] + random.uniform(-radius, radius)
        z_loc = character_root[2] + random.uniform(-radius, radius)
        location = (x_loc, y_loc, z_loc)
        rotation = (0, 0, 0)
        bpy.ops.object.lamp_add(
            type=type, view_align=False, location=location, rotation=rotation
        )
    else:
        raise Exception("{} is an Invalid Lamp Type".format(type))
    return


def renderImage(resolution, file_extension, dir, filename):
    """
    Render Image at Current Camera Config to Disk
    :param resolution: resolution of image render
    :param file_extension: file extension type for export (JPEG)
    :param dir: directory to Export img
    :param filename = name of export image
    :return:
    """
    # render resolution
    bpy.context.scene.render.resolution_x = resolution
    bpy.context.scene.render.resolution_y = resolution
    bpy.data.scenes["Scene"].render.resolution_percentage = 100
    # image settings
    bpy.context.scene.render.image_settings.color_mode = "RGB"
    bpy.context.scene.render.image_settings.file_format = file_extension
    # file name (will automatically add .jpg)
    bpy.context.scene.render.filepath = dir + "/temp/" + filename
    # set start/end animation to frame 2
    bpy.data.scenes["Scene"].frame_start = 2
    bpy.data.scenes["Scene"].frame_end = 2
    # render image
    bpy.ops.render.render(write_still=True)
    return


# Start Blender Creation
delete("All")

# MHX2 CHARACTER ----------
# Find mhx2 Name
mhx2_name = [
    key for key in os.listdir(data_out + "/temp") if "mhx2" in key and len(key) == 16
][0][:-4]
# mhx2_name = '1'
# Get mhx2 object name in blender (First letter capitalize, all others lowercase)
mhx2_lower = mhx2_name.lower()
mhx2_blendername = mhx2_lower.capitalize()
# Import mhx2 Character
try:
    bpy.ops.import_scene.makehuman_mhx2(
        filepath=(data_out + "/temp/" + mhx2_name + "mhx2/" + mhx2_name + ".mhx2")
    )
except:
    raise Exception("Blender MHX2 Import Error")

# POSE ----------
# Add Random Pose
try:
    equipRandomPose()
except:
    raise Exception("Pose Equip Blender Error")

# JOINT GLOBAL COORDINATES ----------
# Create list of joint objects and their global coordinates
jointsList = []
for elem in jointsTitlesList:
    jointsList.append(Joint(elem[0], elem[1], elem[2]))
for elem in jointsList:
    elem.get_gcs(mhx2_blendername)

# Initial Random Yaw
# Camera Yaw About Z-Axis Perpendicular to Ground Surface
z_camera_yaw = random.uniform(0, 2 * np.pi)
# Change to Object Mode for First Iteration
bpy.ops.object.mode_set(mode="OBJECT")

# 10 Images/Joints by Rotating Camera About Horizon
for index in range(10):
    # CAMERA ----------
    # Create Camera with Subject in Frame
    createCamera(jointsList, z_camera_yaw)
    # Set Camera Parameters
    scene = context.scene
    # Set camera = current camera object
    camera = bpy.data.objects["Camera"]

    # LIGHTING ----------
    # Create sun Lamp 70 Percent of the Time: If not create point
    if random.random() < 0.7:
        createRandomLamp("SUN", mhx2_blendername, z_camera_yaw)
    else:
        createRandomLamp("POINT", mhx2_blendername, 0)
    # Create between 0 and 2 point Lamps
    for _ in range(random.randint(0, 2)):
        createRandomLamp("POINT", mhx2_blendername, 0)

    # RENDER IMAGE ----------
    # Render Image to Output Directory
    image_name = "test_image"
    renderImage(resolution, "JPEG", data_out, image_name + str(index + 1))

    # JOINT PIXEL COORDINATES ----------
    for elem in jointsList:
        elem.get_pcs(scene, camera, resolution, mhx2_blendername)

    # Write Joint Coordinates to Temporary Output File
    temp_filename = "jointcoordinates"
    with open(
        data_out + "/temp/" + temp_filename + str(index + 1) + ".csv", "w", newline=""
    ) as f:
        for elem in jointsList:
            # Write Joint Coordinates (With Z Offset) + name
            writelist = [
                round(elem.pcs[0], 4),
                round(elem.pcs[1], 4),
                round(elem.pcs[2], 4),
                elem.name,
            ]
            writer = csv.writer(f)
            writer.writerow(writelist)
    f.close()

    # Delete All If Iterations are not Complete
    if index != 9:
        # For Next Iteration
        # Change Yaw by 2pi/10 (10 Images)
        z_camera_yaw += (2 * np.pi) / 10
        # Delete Camera
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_by_type(type="CAMERA")
        bpy.ops.object.delete(use_global=False)
        # Delete Lighting
        bpy.ops.object.select_by_type(type="LAMP")
        bpy.ops.object.delete(use_global=False)
