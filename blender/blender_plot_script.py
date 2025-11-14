import bpy
import csv

csv_file_hardcode = "/Users/dalioshin/projects/exo-planet/data/corrected_output_2025-11-13.csv"

# assume data cleaning done before blender script
def draw_sphere_from_data(path):
    # load data from csv
    with open(path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        star_data = [list(map(float, row[4:])) for row in reader]
    
    star_count = len(star_data)
    
    material = create_glow_material()
    
    # create a archetype unit sphere object that all others will be copies of
    # copies are more efficient here than adding a new object
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, calc_uvs=False, enter_editmode=False)
    archetype_sphere = bpy.context.active_object
    archetype_sphere.name = "Archetype"
    wireframe = archetype_sphere.modifiers.new(type='WIREFRAME', name="Wireframe")
    wireframe.thickness = 0.01
    archetype_sphere.data.materials.append(material)
    # hide the archetype from the final image
    archetype_sphere.hide_set(True)
    archetype_sphere.hide_render = True
    
    for i, row in enumerate(star_data):
        st_rad, st_temp, x, y, z = row
        
        # for each star system make a copy and adjust metrics to fit data
        new_sphere = archetype_sphere.copy()
        new_sphere.location = (x, y, z)
        new_sphere.scale = (st_rad, st_rad, st_rad)
        new_sphere.hide_set(False)
        new_sphere.hide_render = False
        new_sphere.modifiers["Wireframe"].thickness = st_rad * 0.01
        
        bpy.context.collection.objects.link(new_sphere)
        
        print(f"{i} of {star_count}")
                
def create_glow_material():
    """Create a material that glows yellow in the render"""
    mat = bpy.data.materials.new(name="GlowMaterial")
    mat.use_nodes = True
    
    tree = mat.node_tree
    nodes = tree.nodes
    
    # Clear default nodes
    nodes.clear()
    
    # Create emission shader
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs['Color'].default_value = (0.835078, 1, 0.000327989, 1)
    emit.inputs['Strength'].default_value = 5.0
    
    # Create output
    output = nodes.new("ShaderNodeOutputMaterial")
    
    # Link
    tree.links.new(output.inputs['Surface'], emit.outputs['Emission'])
    
    return mat

if __name__ == "__main__":        
    draw_sphere_from_data(csv_file_hardcode)