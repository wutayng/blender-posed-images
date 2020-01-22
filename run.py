
import os
import time
import pandas
start_time = time.time()

os.system("/Applications/Blender/blender.app/Contents/MacOS/blender --background \
        --python \
        /Users/warrentaylor/Desktop/movement/synthetic-makehuman/blender-posed-images/blender-scripts/run-blender.py")

print(
    "Competeted! Total Time Elapsed: {} Minutes".format(
        round((time.time() - start_time) / 60), 4
    )
)