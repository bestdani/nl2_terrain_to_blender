import os
import pathlib

import re

LOG_PATH = 'appdata/com.nolimitscoaster.nolimits2/nolimits2_log.txt'
DATA_STRING = '###TERRAIN DATA###\n'


def get_terrain_data(data):
    pass


def get_nl2_log_file():
    environ_path = pathlib.Path(LOG_PATH)
    base = environ_path.parts[0]
    relative_path_to_log = pathlib.Path('/'.join(environ_path.parts[1:]))
    path_base = pathlib.Path(os.environ[base])
    path_to_log = path_base / relative_path_to_log
    return str(path_to_log)


def convert_to_float(value):
    try:
        return float(value)
    except ValueError:
        text = 'could not convert {} to float'.format(value)
        raise ValueError(text)


def get_data_from_file(file_name):
    with open(file_name) as file_handle:
        content = file_handle.read()

    matches = list(re.finditer(DATA_STRING, content))
    try:
        data_start = matches[-2].end()
        data_end = matches[-1].start()
    except IndexError:
        raise IOError("could not find data in nl2_log.txt")

    data_string = content[data_start:data_end]
    row_string = data_string.split('\n')
    data = []
    for row in row_string:
        cols = row.split(';')[:-1]
        if (len(cols) > 0):
            data.append([convert_to_float(entry) for entry in cols])
    return data


def data_from_nl2_log():
    file = get_nl2_log_file()
    data = get_data_from_file(file)
    return data


def run_external():
    data = data_from_nl2_log()
    dimensions = (len(data), len(data[0]))
    vertices = transform_data_to_vertices(data, dimensions)
    faces = get_faces(dimensions)
    print(faces[0:2])
    print(vertices[0])
    print(vertices[1])
    print(vertices[770])
    print(vertices[769])


def transform_data_to_vertices(data, dimensions):
    offset = (-dimensions[0] // 2 + 1, -dimensions[1] // 2 + 1)
    vertices = []
    for x, rows in enumerate(data):
        for y, z, in enumerate(rows):
            vertices.append(
                (
                    2 * (x + offset[0]),
                    2 * (y + offset[1]),
                    z
                )
            )
    return vertices


def get_faces(dimensions):
    faces = []
    for y_offset in range(dimensions[1] - 1):
        y_start = y_offset * dimensions[0]
        for vertex_index in range(y_start, y_start + dimensions[0] - 1):
            quad_vertices = [vertex_index + 1,
                             vertex_index,
                             vertex_index + dimensions[1],
                             vertex_index + dimensions[1] + 1
                             ]
            faces.append(quad_vertices)
    return faces


def create_object_from_data(data):
    dimensions = (len(data), len(data[0]))
    vertices = transform_data_to_vertices(data, dimensions)
    faces = get_faces(dimensions)
    mesh = bpy.data.meshes.new('nl2terrain')
    mesh.from_pydata(vertices, [], faces)
    for face in mesh.polygons:
        face.use_smooth = True
    obj = bpy.data.objects.new('nl2terrain', mesh)
    bpy.context.scene.objects.link(obj)


def run_in_blender():
    class LoadTerrainOperator(bpy.types.Operator):
        bl_idname = "wm.load_terrain"
        bl_label = "Load Terrain"

        def execute(self, context):
            try:
                data = data_from_nl2_log()
            except IOError:
                message = "could not find data"
                self.report({'ERROR'}, message)
                return {'CANCELLED'}
            create_object_from_data(data)
            return {'FINISHED'}

    bpy.utils.register_class(LoadTerrainOperator)
    bpy.ops.wm.load_terrain()


if __name__ == '__main__':
    try:
        import bpy
    except Exception:
        run_external()
    else:
        run_in_blender()
