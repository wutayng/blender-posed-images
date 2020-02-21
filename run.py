"""
To Create Synthetic/Rendered 3D Human Pose Image Data
"""
import os, time, argparse, shutil
import numpy as np
import lib.core as core
import lib.config as config
from PIL import Image
import random, string
from datetime import datetime
import pickle
from lib.core import mocap

elapsed_time = 0

# Arg Parse for Test vs. Data
parser = argparse.ArgumentParser(description="Blender Image Creation")
parser.add_argument("type", type=str, help="Desired Output: `test` or `data`")
arg_type = vars(parser.parse_args())["type"]
if arg_type != "test" and arg_type != "data":
    raise Exception("Invalid Run Type: Please choose test or data")

# Random Foldername with Date
current_date = datetime.now()
suffix = "".join(random.choices(string.ascii_letters + string.digits, k=4))
folder_date = (
    str(current_date.month)
    + "-"
    + str(current_date.day)
    + "-"
    + str(current_date.year)
    + "-"
    + suffix
)
dir_data_out = config.data_out + "/" + str(folder_date)
if arg_type == "data":
    os.mkdir(dir_data_out)

# Read BVH Poses Pickle to List
mocap_object_list = []
with open(config.dir_bvh_poses + "/cmu-bvh-frames.pickle", "rb") as f:
    for _ in range(pickle.load(f)):
        mocap_object_list.append(pickle.load(f))
print("-Loaded Pickle File of .bvh Poses-")

# Temporary File Locations/Names
image_name = "test_image"
joints_temp_filename = "jointcoordinates"

# Begin Running Blender
i = 1
while i <= config.iterations_total:
    start_time = time.time()
    # Create Temporary Directory
    try:
        os.mkdir(config.data_out + "/temp")
    except Exception:
        shutil.rmtree(config.data_out + "/temp")
        os.mkdir(config.data_out + "/temp")

    try:
        # Configure mhx2 folder in output directory for blender to access
        mhx2_name = core.configureMHX2(
            config.dir_humans_assets + "/makeHumans",
            config.dir_humans_assets + "/clothing-patterns",
            config.data_out,
            config.dir_humans_assets + "/makeHumanAssets",
        )

        # Create Random .bvh Pose for blender to access
        core.createRandomPose(mocap_object_list, config.data_out)

        # Run Blender + Blender.py Script
        if arg_type == "test":
            os.system(config.blender_location + " --python ./lib/blender.py")
        elif arg_type == "data":
            # Run Blender
            os.system(
                config.blender_location
                + " --background"
                + " --python ./lib/blender.py"
                + " eclipse >/dev/null"
            )

        print("Blender Iteration Success")
    except Exception:
        # Blender Program Failure
        print("BLENDER FAILURE - DELETING CACHE")
        print("----------")
    else:
        # Check to Made Sure Output Temp Files have 10 Images + 10 csv Files + 1 Makehuman + 1 .bvh Pose
        if len(os.listdir(config.data_out + "/temp")) != 22:
            # Blender Program Failure on Number of Files Output
            print("BLENDER FAILURE OF OUTPUT FILE NUMBER - DELETING CACHE")
            print("----------")
        elif len(os.listdir(config.data_out + "/temp")) == 22:
            # Perform Either ML-Data Writing or Test
            if arg_type == "data":
                # Random Iteration Name
                name_str = "".join(
                    random.choices(string.ascii_letters + string.digits, k=12)
                )
                os.mkdir(dir_data_out + "/" + name_str)
                for index in range(10):
                    # Save Image to Output
                    shutil.copyfile(
                        config.data_out
                        + "/temp/"
                        + image_name
                        + str(index + 1)
                        + ".jpg",
                        dir_data_out
                        + "/"
                        + name_str
                        + "/"
                        + name_str
                        + "-"
                        + str(index + 1)
                        + ".jpg",
                    )

                    # Save Joints to Output
                    shutil.copyfile(
                        config.data_out
                        + "/temp/"
                        + joints_temp_filename
                        + str(index + 1)
                        + ".csv",
                        dir_data_out
                        + "/"
                        + name_str
                        + "/"
                        + name_str
                        + "-"
                        + str(index + 1)
                        + ".csv",
                    )

                # Iteration - Time Taken
                elapsed_time += time.time() - start_time
                print(
                    "{} of {} Iterations Complete, {} Training Samples Made".format(
                        i, config.iterations_total, i * 10
                    )
                )
                print(
                    "** Average Time Per Image/Joint Pair: {} Seconds **".format(
                        (round(elapsed_time / i, 2) / 10)
                    )
                )
                print(
                    "Elapsed Time so Far: {} Minutes or {} Hours".format(
                        round(elapsed_time / 60, 2), round(elapsed_time / 3600, 2)
                    )
                )
                remaining_time = (elapsed_time / i) * (config.iterations_total - i)
                print(
                    "Esimated Time Remaining: {} Minutes or {} Hours".format(
                        round(remaining_time / 60, 2), round(remaining_time / 3600, 2)
                    )
                )
                print("----------")
                # Set to Next Iteration When Successful
                i += 1

            elif arg_type == "test":
                # Read Joints CSV From Blender Run
                which_iteration = random.randint(1, 10)
                image_joints = np.genfromtxt(
                    config.data_out
                    + "/temp/"
                    + joints_temp_filename
                    + str(which_iteration)
                    + ".csv",
                    delimiter=",",
                    dtype=None,
                    encoding="utf8",
                )
                # Perform Test Procedure
                # Draw Joint Circles on Image and Show
                picture = core.overlayJointCoordinates(
                    config.blender_image_resolution,
                    config.img_joint_radius,
                    config.data_out,
                    image_name + str(which_iteration),
                    image_joints,
                )
                picture.show()
                # Create Joints Dataframe
                joints = core.jointsDataFrameGlobal(image_joints)
                # Plot 3D Figure with Joints and Connecting Lines
                core.plot3D(joints)
                shutil.rmtree(config.data_out + "/temp")
                break

    # Delete Blender-Output Cache (mhx2 character, joints csv, test image, pose bvh)
    shutil.rmtree(config.data_out + "/temp")

print("Completed Successfully")
