import sys, os
import logging
import dk4
import common as c

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    failed = True

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        files = []
        outFolder = c.DEFAULT_OUT
        path = sys.argv[1]
        if os.path.isfile(path) and os.path.splitext(path)[1].lower() == ".dk4":
            files.append(path)

        if not os.path.isfile(path):
            outFolder = os.path.join(c.DEFAULT_OUT, os.path.basename(path))
            files = [os.path.join(path, f) for f in os.listdir(path) if os.path.splitext(f)[1].lower() == ".dk4"]

        if len(files) > 0:
            failed = False
            textures = set()
            os.makedirs(outFolder, exist_ok=True)
            for path in files:
                file = os.path.basename(path)[:-4]
                mdl = dk4.getObj(path)
                mdl.name = file
                logging.info(f"{mdl}")
                writter = c.ObjWritter(outFolder, file)
                writter.writeObj(mdl)
                logging.info(f"Successfully wrote .obj/.mtl to {writter.obj}")
                textures.update(writter.usedMtl)
            print("\nLocate the following textures and copy them to the 'textures' subfolder alongside the .obj")
            for t in textures:
                print(f"{t}.bmp -or- {t}.tga")
            input("\nPress Enter to close")

    if failed:
        print(f"Usage: {sys.argv[0]} path_to_file.dk4")
        print(f"Usage: {sys.argv[0]} path_to_folder_containing_dk4 ")
