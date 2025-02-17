from shutil import copy
import sys, os
import logging
import dk4
import common as c

PATH_CLASSES = ["Iridium", "Platinum", "Titanium"]

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) and not os.path.isfile(sys.argv[1]):
        # Create the output directories
        basePath = sys.argv[1]  # Base path of the original directory ([...]\TheCity)
        trackName = os.path.basename(basePath)  # Name of the car (TheCity)
        outPath = os.path.join(c.DEFAULT_OUT, trackName)  # Output path (.\out\TheCity)
        texPath = os.path.join(outPath, "textures")  # Texture path (.\out\TheCity\textures)
        os.makedirs(texPath, exist_ok=True)

        textures = {}
        # copy textures if they don't exist and read them into the textures dictionary
        # Material name case is a mess, rename all dict keys and files to lowercase
        for f in os.listdir(basePath):
            if os.path.splitext(f)[1].lower() in [".bmp", ".tga"]:
                textures[os.path.splitext(f)[0].lower()] = f.lower()
                if not os.path.exists(os.path.join(texPath, f)):
                    copy(os.path.join(basePath, f), os.path.join(outPath, "textures", f.lower()))

        logging.info(f"Starting conversion of track {trackName}")
        for className in PATH_CLASSES:
            append = False
            logging.info(f"Parsing track class {className}")
            writter = c.ObjWritter(outPath, className, textures)
            for f in os.listdir(os.path.join(basePath, className)):
                filePath = os.path.join(basePath, className, f)
                if os.path.isfile(filePath) and ".dk4" in f.lower():
                    logging.info(f"Converting {f}")
                    mdl = dk4.getObj(filePath)
                    mdl.name = f[:-4]
                    writter.writeObj(mdl, append)
                    append = True
                else:
                    logging.info(f"Skipped file {f} (unknown format)")

    else:
        print(f"Usage: {sys.argv[0]} path_to_track_folder")
