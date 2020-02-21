"""
Configuration for run.py Parameters
"""
# Data Parameters
iterations_total = 5  # 10 Images/Joint for Each Iteration

# Test Parameters
blender_image_resolution = 1000  # Pixels (This must also be changed in blender.py)
img_joint_radius = 4  # Joint Coordinate Overlay Circle Radius in Test Image
blender_cam_fov = 0.857556  # FOV Angle Taken from Standard Blender Preset (Rad)

# File Path Locations
blender_location = (
    "/home/warren/Applications/blender-2.79b-linux-glibc219-x86_64/blender"
)
data_out = "/home/warren/data/synthetic-training/blender-data"
dir_humans_assets = "/home/warren/data/synthetic-training/humans-assets"
dir_bvh_poses = "/home/warren/data/synthetic-training/mocap"
