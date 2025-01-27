from __future__ import annotations
import logging
import os
from typing import List, Optional

DEFAULT_OUT = "out"
NO_MTL_NAME = "material"

class Coord3D:
    """
    Class representing a single xyz 3D point
    """

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def translate(self, vector: Coord3D):
        self.x += vector.x
        self.y += vector.y
        self.z += vector.z

    def __str__(self) -> str:
        return f"{self.x} {self.y} {self.z}"


class Material:
    """
    Class representing the information encoded in a .mtl file
    """

    def __init__(self):
        self.start = 0
        self.end = 0
        self.r = 0
        self.g = 0
        self.b = 0
        self.tr = 0
        self.tg = 0
        self.tb = 0
        self.name = ""
        self.transparency = 0  # tr

    def setName(self, name: str):
        """
        Sets the name of the material
        """
        if not name:
            self.name = NO_MTL_NAME
        else:
            self.name = name

    def getDiffuse(self) -> str:
        """
        Gets the diffuse color in "r g b" format
        """
        return f"{self.r} {self.g} {self.b}"

    def getTransparencyColor(self) -> str:
        """
        Gets the transparency color in "r g b" format
        """
        return f"{self.tr} {self.tg} {self.tb}"

    def log(self):
        logging.info(f"Material: s {self.start} \te {self.end}\tn {self.name}")
        logging.info(f"\tRGB {round(self.r, 4)} \t{round(self.g, 4)} \t{round(self.b, 4)} ")
        logging.info(f"\tTRGB  {round(self.tr, 4)} \t{round(self.tg, 4)} \t{round(self.tb, 4)}")


class UV:
    """
    Class that holds a texture's UV coordinates
    """

    def __init__(self, u, v):
        self.u = u
        self.v = v

    def __str__(self):
        return f"{self.u} {self.v}"


class Face:
    """
    Class to hold a face's referenced vertice indexes
    """

    def __init__(self, A: int, B: int, C: int):
        self.A = A
        self.B = B
        self.C = C

    def __str__(self):
        return f"{self.A}/{self.A}/{self.A} {self.B}/{self.B}/{self.B} {self.C}/{self.C}/{self.C}"


class Model:
    """
    Class to represent all that's needed to render a model
    """

    def __init__(self):
        self.verts: List[Coord3D] = []
        self.normals: List[Coord3D] = []
        self.face: List[Face] = []
        self.uvs: List[UV] = []
        self.mats: List[Material] = []
        self.name: str = ""

    def addVert(self, v: Coord3D):
        self.verts.append(v)

    def addNormal(self, n: Coord3D):
        self.normals.append(n)

    def addFace(self, f: Face):
        self.face.append(f)

    def addUV(self, uv: UV):
        self.uvs.append(uv)

    def addMaterial(self, m: Material):
        self.mats.append(m)

    def translateVerts(self, vector: Coord3D):
        """
        Translates all vertices inside the model given the 3D vector
        """
        for v in self.verts:
            v.translate(vector)

    def merge(self, child: Model):
        """
        Merges a child model into this model. Offsets the face and material indexes in the process.
        """
        self.mats.pop()  # remove child's dummy material
        pVerts = len(self.verts)  # num of verts
        pFaces = len(self.face)  # num of faces

        self.verts.extend(child.verts)
        self.normals.extend(child.normals)
        self.uvs.extend(child.uvs)
        # faces indexes have to be incremented
        for cf in child.face:
            self.face.append([f + pVerts for f in cf])
        # increment material indexes
        for cm in child.mats:
            logging.debug(f"Shifting material from {cm.start} - {cm.end} - {cm.start}")
            cm.start += pFaces
            cm.end += pFaces
            logging.debug(f" Shifted material  to  {cm.start} - {cm.end}")
            self.mats.append(cm)

    def __str__(self):
        return f"{self.name} => Model data:\n{len(self.verts)} verts\n{len(self.normals)} normals\n{len(self.face)} faces\n{len(self.uvs)} uvs\n{len(self.mats)} materials\n"


class ObjWritter:
    """
    Class needed to write and keep track of multiple objects within an .obj file
    """

    def __init__(self, path: str, fileName: str, textures: Optional[dict] = {}):
        """
        Args:
            path (str): Folder to store the files to.
            file (str): Name of the .obj/.mtl files.
        """
        self.obj = os.path.join(path, fileName) + ".obj"
        self.mtl = os.path.join(path, fileName) + ".mtl"
        self.fileName = fileName
        self.lastMatInd = 0  # index to rename materials without name to distinguish them
        self.usedMtl = set()
        self.vertInd = 0
        self.textureList = textures

    def writeObj(self, mdl: Model, append: bool = False):
        """
        Function to write the data from a Model class to a wavefront .obj/.mtl file
        Args:
            mdl (Model): The model data to write.
            append (bool): If true it will append to the existing file.
                        Done to append multiple objects into a single .mdl
        """
        mode = "a"
        # Remove possible old files if not appending
        if not append:
            if os.path.exists(self.obj):
                os.remove(self.obj)
            if os.path.exists(self.mtl):
                os.remove(self.mtl)
            mode = "w"
        with open(self.obj, mode) as obj, open(self.mtl, mode) as mtl:
            if not append:
                obj.write(f"# {self.fileName} {mdl.name} dk4 file converted to obj\n")
                obj.write(f"mtllib {self.fileName}.mtl\n")  # material file reference

            obj.write(f"# {mdl.name} object data\n")
            obj.write(f"o {mdl.name}\n")

            # write vertices as XYZ
            obj.write(f"# {len(mdl.verts)} verts\n")
            for v in mdl.verts:
                obj.write(f"v {v}\n")
            obj.write("\n")

            # write UVs as UV
            obj.write(f"# {len(mdl.uvs)} UVs\n")
            for uv in mdl.uvs:
                obj.write(f"vt {uv}\n")
            obj.write("\n")

            # write normals
            obj.write(f"# {len(mdl.normals)} normals\n")
            for n in mdl.normals:
                obj.write(f"vn {n}\n")
            obj.write("\n")

            # write the faces
            # matInd - index for the current material within the Model
            obj.write(f"# {len(mdl.face)} faces\n")
            matInd = 0
            for i in range(len(mdl.face)):
                # When the index for the current face is within the face range for the next
                # material group write "usemtl {name}" before starting to write face groups
                # Also write the material information into the .mtl file when that happens
                if i >= mdl.mats[matInd].start:
                    matName = mdl.mats[matInd].name
                    if matName == NO_MTL_NAME:
                        obj.write(f"usemtl {NO_MTL_NAME}{self.lastMatInd}\n")
                        mtl.write(f"newmtl {NO_MTL_NAME}{self.lastMatInd}\n")
                        mtl.write(f"\tKd {mdl.mats[matInd].getDiffuse()}\n")
                        mtl.write(f"\tTf {mdl.mats[matInd].getTransparencyColor()}\n")
                        mtl.write(f"\tTr {mdl.mats[matInd].transparency}\n")
                        mtl.write(f"\td {1-mdl.mats[matInd].transparency}\n")
                        self.lastMatInd += 1
                    else:
                        # Named materials are always a reference to a texture of the same name with
                        # either a .bmp or .tga extension. If no texture dict is supplied, assume .bmp
                        # Some filenames have a different case to the material name
                        # (i.e. L_Windows1 => L_windows1), use lowercase keys
                        if matName not in self.usedMtl:
                            mtl.write(f"newmtl {matName}\n")
                            mtl.write(f"\tmap_Kd textures/{self.textureList.get(matName.lower(), matName + '.bmp')}\n")
                            self.usedMtl.add(matName)
                        obj.write(f"usemtl {matName}\n")
                    matInd += 1
                # The face groups taking into account the previous written object indexes
                obj.write(
                    "f "
                    f"{mdl.face[i].A + self.vertInd}/{mdl.face[i].A + self.vertInd}/{mdl.face[i].A + self.vertInd} "
                    f"{mdl.face[i].B + self.vertInd}/{mdl.face[i].B + self.vertInd}/{mdl.face[i].B + self.vertInd} "
                    f"{mdl.face[i].C + self.vertInd}/{mdl.face[i].C + self.vertInd}/{mdl.face[i].C + self.vertInd}"
                )
                obj.write("\n")
            # Offset the current vertex index by the amount of vertices read
            self.vertInd += len(mdl.verts)

            obj.write("\n")
