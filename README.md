# dk4-converter

This repo contains python scripts to convert the dk4 models from Melbourne House/Beam Software 1998 game Dethkarz into wavefront obj.

## Usage

The converted files will be saved to the folder specified in `common.py`, by default `.\out\`

To convert tracks or cars the script expects to be given a folder with all the content extracted directly from the data zip (instructions below). The source files/folder won't be deleted.

Car/track folder structure:

    <folder>
    ├ Iridium
    |  ┕ <files>
    ├ Platinum
    |  ┕ <files>
    ├ Titanium
    |  ┕ <files>
    ┕ <files>

### Converting tracks

    convert_track.py <path_to_track_folder>

### Converting cars

    convert_car.py <path_to_car_folder>


### Converting files

For a single file:

    convert_dk4.py <path_to_dk4_file>

For a folder containing dk4 files:

    convert_dk4.py <path_to_folder>

## Extracting files

0. Acquire and install a copy of the game from GoG, Steam, or retail.
1. Open `<path-to-game>\Data\Dethkarz.dkz` as a zip file.
2. Navigate to `Data\Models` within the zip.
3. Extract the desired files/folders.
