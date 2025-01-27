from shutil import copy
import sys, os
import logging
import dk4
import common as c

PATH_CLASSES = ["Iridium", "Platinum", "Titanium"]
PATH_CARBODY = "Carbody"
PATH_MODEL = "lod0.dk4"
PATH_WHEELS = ["Wheelfl", "Wheelfr", "Wheelrl", "Wheelrr"]
PATH_PARAMS = "dkcar.txt"

WL_SHARED = ["Fast", "Steady"]
SECRET = "Secret"


def readParams(path):
    wheels = {}
    with open(path, "r") as f:
        lines = f.readlines()

    x = float(lines[6].split("\t")[-1])
    y = float(lines[7].split("\t")[-1])
    z = float(lines[8].split("\t")[-1])
    wheels[PATH_WHEELS[0]] = c.Coord3D(x, z, -y)  # FL
    wheels[PATH_WHEELS[1]] = c.Coord3D(x, z, y)  # FR

    x = float(lines[11].split("\t")[-1])
    y = float(lines[12].split("\t")[-1])
    z = float(lines[13].split("\t")[-1])
    wheels[PATH_WHEELS[2]] = c.Coord3D(x, z, -y)  # RL
    wheels[PATH_WHEELS[3]] = c.Coord3D(x, z, y)  # RR
    return wheels


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) and not os.path.isfile(sys.argv[1]):
        # Create the output directories
        basePath = sys.argv[1]  # Base path of the original directory ([...]\Fast)
        carName = os.path.basename(basePath)  # Name of the car (Fast)
        outPath = os.path.join(c.DEFAULT_OUT, carName)  # Output path (.\out\Fast)
        texPath = os.path.join(outPath, "textures")  # Texture path (.\out\Fast\textures)
        if not os.path.exists(outPath):
            os.mkdir(outPath)
        if not os.path.exists(texPath):
            os.mkdir(texPath)

        logging.info(f"Starting conversion of car {carName}")
        if carName != SECRET:
            logging.info("Car is not secret")
            paths = [p for p in PATH_CLASSES]
        else:
            paths = [""]
            logging.info("Car is secret")

        for className in paths:
            logging.info(f"Parsing {carName} {className}")
            if className:
                writter = c.ObjWritter(outPath, className)
            else:
                writter = c.ObjWritter(outPath, carName)

            # Parse the main car body
            carbody = dk4.getObj(os.path.join(basePath, className, PATH_CARBODY, PATH_MODEL))
            carbody.name = className

            # Write the Carbody before appending wheels
            writter.writeObj(carbody)

            # Read the position of the wheels from dkcar.txt
            params = readParams(os.path.join(basePath, className, PATH_PARAMS))

            # Parse the wheels
            # For some reason the files inside the Iridium folder are in .dk3 format which are lower poly
            # and different from those shown in-game (maybe leftovers from a previous version?)
            # assume Platinum class wheels as Titanium's are bigger
            for wheelName in PATH_WHEELS:
                if className == PATH_CLASSES[0]:
                    # when Iridium, set path to platinum wheels
                    path = os.path.join(basePath, PATH_CLASSES[1], wheelName, PATH_MODEL)
                else:
                    path = os.path.join(basePath, className, wheelName, PATH_MODEL)

                # Read the model data
                wheel = dk4.getObj(path)
                wheel.name = wheelName

                # Offset all vertices by the values read from the parameters
                wheel.translateVerts(params[wheelName])

                # Append the wheel to the Carbody .obj
                writter.writeObj(wheel, True)

        # copy textures if they don't exist
        for f in os.listdir(basePath):
            if os.path.splitext(f)[1] == ".bmp" and not os.path.exists(os.path.join(texPath, f)):
                copy(os.path.join(basePath, f), os.path.join(outPath, "textures", f))
    else:
        print(f"Usage: {sys.argv[0]} path_to_car_folder")
