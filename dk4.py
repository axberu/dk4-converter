from struct import unpack

import common as c

# Data offsets, padding, etc
HEADER_END = 0xBC  # Position where the fixed size header ends
COUNT_F = 0x80  # position to read num of faces (int)
COUNT_V = 0x88  # position to read num of vertex (int)
COUNT_M = 0x94  # position to read num of materials (int)
PAD_FACE = 14  # bytes of padding between faces
PAD_MAT = 24  # bytes of paddingg between materials


def readShort(stream) -> int:
    buff = stream.read(2)
    return unpack("<h", buff)[0]


def readInt(stream) -> int:
    buff = stream.read(4)
    return unpack("<i", buff)[0]


def readFloat(stream) -> float:
    buff = stream.read(4)
    return unpack("<f", buff)[0]


def readString(stream) -> str:
    # Material names are encoded as fixed 16 byte
    return stream.read(16).decode().strip("\0")


def readCoord3D(stream) -> c.Coord3D:
    x = readFloat(stream)
    y = readFloat(stream)
    z = readFloat(stream)
    return c.Coord3D(x, z, -y)


def readUV(stream) -> c.UV:
    u = readFloat(stream)
    v = readFloat(stream)
    return c.UV(u, -v + 1)


def readFaces(stream) -> c.Face:
    tA = readShort(stream) + 1
    tB = readShort(stream) + 1
    tC = readShort(stream) + 1
    return c.Face(tA, tB, tC)


def getObj(file: str) -> c.Model:
    mdl = c.Model()
    numVerts = 0
    numFaces = 0
    numMats = 0
    with open(file, "rb") as dk4:
        # read number of verts/faces
        dk4.seek(COUNT_F)
        numFaces = readInt(dk4)
        dk4.seek(COUNT_V)
        numVerts = readInt(dk4)
        dk4.seek(COUNT_M)
        numMats = readInt(dk4)

        # read verts, normals, uvs
        dk4.seek(HEADER_END + 8)
        for _ in range(numVerts):
            mdl.addVert(readCoord3D(dk4))
            mdl.addNormal(readCoord3D(dk4))
            mdl.addUV(readUV(dk4))

        # read face indexes
        # After reading all the vertices skip 8 bytes for the "identifier"
        # dk4.seek(HEADER_END + 32 * numVerts + 8)
        dk4.seek(8, 1)
        for _ in range(numFaces):
            mdl.addFace(readFaces(dk4))
            dk4.seek(PAD_FACE, 1)

        # materials
        # After reading all the faces skip 8 bytes for the "identifier"
        # dk4.seek(HEADER_END + 32 * numVerts + 8 + numFaces * 20 + 8)
        dk4.seek(8, 1)
        for _ in range(numMats):
            mat = c.Material()
            # faces its applied to
            mat.start = readInt(dk4)
            mat.end = readInt(dk4)
            # face color
            mat.r = readFloat(dk4)
            mat.g = readFloat(dk4)
            mat.b = readFloat(dk4)
            # Transmission Color (?)
            dk4.seek(3 * 4, 1)
            mat.tr = readFloat(dk4)
            mat.tg = readFloat(dk4)
            mat.tb = readFloat(dk4)
            dk4.seek(4, 1)
            mat.setName(readString(dk4))  # name
            dk4.seek(8, 1)
            mat.transparency = readFloat(dk4)  # transparency
            mdl.addMaterial(mat)
            dk4.seek(PAD_MAT, 1)

        # append dummy material
        mat = c.Material()
        mat.start = 0xFFFF + 1
        mat.setName("none")
        mdl.addMaterial(mat)
    return mdl
