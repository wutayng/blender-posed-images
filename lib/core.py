"""
Functions for run.py
"""
import os, shutil, random, re
import lib.config as config
from numpy import sum
from numpy.random import choice
import numpy as np
from PIL import Image, ImageDraw
from lib.transforms import RGBTransform
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def findRandomMHX2(dir_mhx2):
    """
    Choose a Random .mhx2 File from the makeHumans directory
    makeHumans directory may contain subdirs, each with .mhx2 characters
    :return: folderpath for .mhx2 character
    :return: name (str) of mhx2 folder/file
    """
    # Weighted Directory Choice Based on the Number of Elements
    num_contents = []
    basedir_list = []
    for elem in os.listdir(dir_mhx2):
        if os.path.isdir(os.path.join(dir_mhx2, elem)):
            num_contents.append(len(os.listdir(dir_mhx2 + "/" + elem)))
            basedir_list.append(dir_mhx2 + "/" + elem)
    probabilities = [el / sum(num_contents) for el in num_contents]
    base_dir = choice(basedir_list, 1, p=probabilities)
    mhx2_str = choice(os.listdir(base_dir[0]))
    folderpath = base_dir[0] + "/" + mhx2_str
    return folderpath, mhx2_str


def findRandomPattern(dir_patterns):
    """
    Choose a Pattern File from the textures directory
    textures directory containd subdirs, each with textures
    :return: full filepath for pattern
    """
    # Weighted Directory Choice Based on the Number of Elements
    num_contents = []
    for elem in os.listdir(dir_patterns):
        num_contents.append(len(os.listdir(dir_patterns + "/" + elem)))
    probabilities = [el / sum(num_contents) for el in num_contents]
    folder_choice = choice(os.listdir(dir_patterns), 1, p=probabilities)
    pattern_choice = choice(os.listdir(dir_patterns + "/" + folder_choice[0]))
    return dir_patterns + "/" + folder_choice[0] + "/" + pattern_choice


def configureMHX2(dir_mhx2, dir_patterns, data_out, dir_mhx2assets):
    """
    Copy Random Makehuman from Storage and Alter Textures
    Place in output directory for blender input
    :return: mhx2 name for deletion later
    """
    # Copy Random Makehuman to Output
    mhx2_folder_path, mhx2_name = findRandomMHX2(dir_mhx2)
    # Copy MHX2 Folder to Blender Output
    shutil.copytree(mhx2_folder_path, data_out + "/temp/" + mhx2_name + "mhx2")
    # Find Diffuse Files in mhx2 Character
    mhx2_diffuse_textures = [
        key
        for key in os.listdir(data_out + "/temp/" + mhx2_name + "mhx2/textures")
        if "diffuse" in key
    ]

    # Find all Hair Name Strings
    hair_list = []
    for gender_elem in ["male/", "female/"]:
        for common_elem in ["common", "medium", "uncommon"]:
            for elem in os.listdir(
                dir_mhx2assets + "/hair/" + gender_elem + common_elem
            ):
                hair_list.append(elem)
        if gender_elem == "male/":
            for elem in os.listdir(dir_mhx2assets + "/hair/" + gender_elem + "beards"):
                hair_list.append(elem)

    # Alter Diffuse Textures in mhx2 Package
    for elem in mhx2_diffuse_textures:
        # Keep a % of Clothes UNCHANGED
        percentage_unchanged = 2
        tex_choice = random.randint(1, 100)
        if tex_choice <= percentage_unchanged:
            pass
        elif tex_choice > percentage_unchanged:
            # Alter Hair Color Diffuse Images
            if any(hair_str in elem for hair_str in hair_list):
                current_hair = Hair(
                    data_out + "/temp/" + mhx2_name + "mhx2/textures/" + elem
                )
                current_hair.randomizeHairTexture()
                pass

            # Replace Diffuse Textures with Random Pattern Images for Non-Hair Images
            else:
                # Get Image Path
                random_pattern_path = findRandomPattern(dir_patterns)
                random_pattern = Image.open(random_pattern_path)
                bbox = random_pattern.getbbox()
                cropped_image = random_pattern.crop(bbox)
                # Crop to Square
                sqr_width = np.ceil(
                    np.sqrt(cropped_image.size[0] * cropped_image.size[1])
                ).astype(int)
                fit_pattern = cropped_image.resize((sqr_width, sqr_width))
                try:
                    fit_pattern.save(
                        data_out + "/temp/" + mhx2_name + "mhx2/textures/" + elem
                    )
                except IOError:
                    raise Exception(
                        "PIL Error: Cannot create png for {}", random_pattern_path
                    )
        else:
            raise Exception(
                "{} - choice value for not changing textures is invalid".format(
                    tex_choice
                )
            )
    return mhx2_name


# Insert Mocap File Class to Load Pickle Mocap
class mocap:
    def __init__(self, name, header):
        self.name = name
        self.header = header
        self.frames = []


def createRandomPose(mocap_object_list, data_out):
    """
    Save pose choice from list (via pickle) it to output location
    :param mocap_object_list: List generated from Pickle
    :param data_out: output directory
    :return:
    """
    # Random Video File
    mocap_object = random.choice(mocap_object_list)
    # Random Frame
    frame_no = random.randint(0, len(mocap_object.frames))
    frame = mocap_object.frames[frame_no]
    outfile = open(data_out + "/temp/temp_bvh_pose.bvh", "w")
    outfile.write(mocap_object.header + mocap_object.frames[frame_no])
    outfile.close()
    return


def overlayJointCoordinates(resolution, radius, data_out, image_name, image_joints):
    """
    # Alter Output Image (Joint Pixel Color)
    :param: resolution - x/y resolution of output image
    :param: dirs for dependent files
    :param: radius - radius of overlaid circle on image
    :return: PIL picture
    """
    picture = Image.open(data_out + "/temp/" + image_name + ".jpg")
    draw = ImageDraw.Draw(picture)
    for elem in image_joints:
        draw.ellipse(
            xy=(
                int(elem[0]) - radius,
                int(resolution - elem[1]) - radius,
                int(elem[0]) + radius,
                int(resolution - elem[1]) + radius,
            ),
            fill=(255, 0, 0),
        )
    return picture


def linePlotCoords(joints, joint1_name, joint2_name):
    """
    Helper Function for plot3D
    :param joints: Pandas Dataframe of Joints
    :param joint1_name: name of joint 1
    :param joint2_name: name of joint 2
    :return: Line Coordinates in form [[x1, x2], [y1, y2], [z1, z2]]
    """
    x = [joints.loc[joint1_name]["x"], joints.loc[joint2_name]["x"]]
    y = [joints.loc[joint1_name]["y"], joints.loc[joint2_name]["y"]]
    z = [joints.loc[joint1_name]["z"], joints.loc[joint2_name]["z"]]
    return [x, y, z]


def plot3D(joints):
    """
    Matplotlib 3D Scatter of Human Character
    :param joints: Pandas Dataframe of Joints
    :return:
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    # Recover int values from joint list
    x = joints["x"]
    y = joints["y"]
    z = joints["z"]
    ax.scatter(x, y, z)
    # Create cubic bounding box to simulate equal aspect ratio
    max_range = np.array(
        [x.max() - x.min(), y.max() - y.min(), z.max() - z.min()]
    ).max()
    xb = 0.5 * max_range * np.mgrid[-1:2:2, -1:2:2, -1:2:2][0].flatten() + 0.5 * (
        x.max() + x.min()
    )
    yb = 0.5 * max_range * np.mgrid[-1:2:2, -1:2:2, -1:2:2][1].flatten() + 0.5 * (
        y.max() + y.min()
    )
    zb = 0.5 * max_range * np.mgrid[-1:2:2, -1:2:2, -1:2:2][2].flatten() + 0.5 * (
        z.max() + z.min()
    )
    # Comment or uncomment following both lines to test the fake bounding box:
    for bound_x, bound_y, bound_z in zip(xb, yb, zb):
        ax.plot([bound_x], [bound_y], [bound_z], "w")

    # Connecting Lines
    # Create List of Connecting Lines
    line_list = []
    main_body_linewidth = 3
    limbs_linewidth = 1.5
    support_linewidth = 0.5
    # Main Body
    main_body_color = "r"
    line_list.append(
        [
            linePlotCoords(joints, "pelvis", "lower_back"),
            main_body_color,
            main_body_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "lower_back", "mid_back"),
            main_body_color,
            main_body_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "mid_back", "spine"),
            main_body_color,
            main_body_linewidth,
        ]
    )
    line_list.append(
        [linePlotCoords(joints, "spine", "neck"), main_body_color, main_body_linewidth]
    )
    line_list.append(
        [
            linePlotCoords(joints, "neck", "upper_neck"),
            main_body_color,
            main_body_linewidth,
        ]
    )
    line_list.append(
        [linePlotCoords(joints, "spine", "sc_left"), main_body_color, support_linewidth]
    )
    line_list.append(
        [
            linePlotCoords(joints, "spine", "sc_right"),
            main_body_color,
            support_linewidth,
        ]
    )
    line_list.append(
        [linePlotCoords(joints, "sc_left", "neck"), main_body_color, support_linewidth]
    )
    line_list.append(
        [linePlotCoords(joints, "sc_right", "neck"), main_body_color, support_linewidth]
    )
    line_list.append(
        [
            linePlotCoords(joints, "upper_neck", "head"),
            main_body_color,
            main_body_linewidth,
        ]
    )
    line_list.append(
        [linePlotCoords(joints, "head", "crown"), main_body_color, main_body_linewidth]
    )
    # Arms
    arms_color = "b"
    line_list.append(
        [
            linePlotCoords(joints, "sc_left", "shoulder_left"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "shoulder_left", "elbow_left"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "elbow_left", "wrist_left"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [linePlotCoords(joints, "wrist_left", "hand_left"), arms_color, limbs_linewidth]
    )
    line_list.append(
        [
            linePlotCoords(joints, "hand_left", "finger_base_left"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "hand_left", "thumb_base_left"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "thumb_base_left", "thumb_left"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "finger_base_left", "finger_left"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "sc_right", "shoulder_right"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "shoulder_right", "elbow_right"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "elbow_right", "wrist_right"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "wrist_right", "hand_right"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "hand_right", "finger_base_right"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "hand_right", "thumb_base_right"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "thumb_base_right", "thumb_right"),
            arms_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "finger_base_right", "finger_right"),
            arms_color,
            limbs_linewidth,
        ]
    )
    # Arms
    legs_color = "g"
    line_list.append(
        [linePlotCoords(joints, "pelvis", "hip_left"), legs_color, limbs_linewidth]
    )
    line_list.append(
        [linePlotCoords(joints, "hip_left", "knee_left"), legs_color, limbs_linewidth]
    )
    line_list.append(
        [linePlotCoords(joints, "knee_left", "ankle_left"), legs_color, limbs_linewidth]
    )
    line_list.append(
        [linePlotCoords(joints, "ankle_left", "foot_left"), legs_color, limbs_linewidth]
    )
    line_list.append(
        [linePlotCoords(joints, "foot_left", "toe_left"), legs_color, limbs_linewidth]
    )
    line_list.append(
        [linePlotCoords(joints, "pelvis", "hip_right"), legs_color, limbs_linewidth]
    )
    line_list.append(
        [linePlotCoords(joints, "hip_right", "knee_right"), legs_color, limbs_linewidth]
    )
    line_list.append(
        [
            linePlotCoords(joints, "knee_right", "ankle_right"),
            legs_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [
            linePlotCoords(joints, "ankle_right", "foot_right"),
            legs_color,
            limbs_linewidth,
        ]
    )
    line_list.append(
        [linePlotCoords(joints, "foot_right", "toe_right"), legs_color, limbs_linewidth]
    )

    # Plot all Lines
    for elem in line_list:
        ax.plot(elem[0][0], elem[0][1], elem[0][2], color=elem[1], linewidth=elem[2])

    plt.grid()
    ax.view_init(elev=90, azim=-90)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.show()
    return


def jointsDataFrameGlobal(image_joints):
    """
    Create Dataframe of Joint Coordinates & Convert Perspective Camera View to Global Coordinates
    :param image_joints: genfromtxt input of character joints
    :return: Global JointsDataFrame
    """
    data = []
    joint_names = []
    root_pelvis_z = image_joints[0][2]
    for elem in image_joints:
        # Convert Perspective to Global
        # FOV Angle Taken from Standard Blender Preset
        camera_width = np.tan(config.blender_cam_fov / 2) * elem[2] * 2
        x_glob = ((elem[0] / config.blender_image_resolution) - 0.5) * camera_width
        y_glob = ((elem[1] / config.blender_image_resolution) - 0.5) * camera_width
        z_glob = (elem[2] - root_pelvis_z) * -1
        data.append([x_glob, y_glob, z_glob])
        joint_names.append(elem[3])
    # Create the pandas DataFrame
    df = pd.DataFrame(data, columns=["x", "y", "z"])
    df.index = joint_names
    return df


# Hair Modifications
class Hair:
    hair_colors = {
        # natural hair colors
        "midnightBlack": (9, 8, 6),
        "offBlack": (44, 34, 43),
        "darkestBrown": (59, 48, 36),
        "medDarkBrown": (78, 67, 63),
        "chestnutBrown": (80, 68, 68),
        "lightChestnutBrown": (106, 78, 66),
        "darkGoldenBrown": (85, 72, 56),
        "lightGoldenBrown": (167, 133, 106),
        "darkHoneyBlonde": (184, 151, 120),
        "bleachedBlonde": (220, 208, 186),
        "lightAshBlonde": (222, 188, 153),
        "lightAshBrown": (151, 121, 97),
        "lightestBlonde": (230, 206, 168),
        "paleGoldenBlonde": (229, 200, 168),
        "strawberryBlonde": (165, 107, 70),
        "lightAuburn": (145, 85, 61),
        "darkAuburn": (83, 61, 50),
        "darkestGray": (115, 99, 90),
        "mediumGray": (183, 166, 158),
        "lightGray": (214, 196, 194),
        "whiteBlonde": (255, 240, 225),
        "platinumBlonde": (80, 68, 68),
        "russetRed": (141, 74, 67),
        "terraCotta": (181, 82, 57),
        # non-natural hair colors
        "green": (20, 180, 40),
        "pink": (200, 0, 200),
        "red": (153, 51, 0),
        "blue": (153, 204, 255),
    }

    def __init__(self, texture_path):
        self.texture_path = texture_path
        self.hair_color = random.choice(list(Hair.hair_colors))

    def randomizeHairTexture(self):
        """
        Alter .png Texture File for Hair Asset
        Change Color to TBD
        """
        img = Image.open(self.texture_path)
        # Take original color out of .png by conversion to BW and back
        img = img.convert("LA")
        img = img.convert("RGB")
        # 0.3 mu random normal mix factor (0 is no color input, 1 is solid color)
        mix_factor = np.random.normal(0.6, 0.1)
        img = (
            RGBTransform()
            .mix_with(Hair.hair_colors[self.hair_color], factor=mix_factor)
            .applied_to(img)
        )
        # save - overwrite current .png texture file
        img.save(self.texture_path)
        return
