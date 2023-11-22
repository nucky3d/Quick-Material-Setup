bl_info = {
    "name": "Quick Material Setup",
    "blender": (3, 6, 0),
    "category": "Material",
    "location": "Properties > Material",
    "description": "Quickly import textures as materials",
    "author": "Nucky3d",
    "version": (1, 0),
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "",
}

from tokenize import group
import typing
import bpy
from bpy_extras.io_utils import ImportHelper
import os
from bpy.types import Context, Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty
from bpy.app.handlers import persistent
from bpy.types import (
    Operator,
    Menu,
)

# Settings
class OBJECT_OT_addon_prefs_example(Operator):
    bl_idname = "object.addon_prefs_example"
    bl_label = "Add-on Preferences Example"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        info = ("Path: %s, Number: %d, Boolean %r" %
                (addon_prefs.filepath, addon_prefs.number, addon_prefs.boolean))

        self.report({'INFO'}, info)
        print(info)

        return {'FINISHED'}

class FastMaterialsPreferences(bpy.types.PropertyGroup):
    texture_prefixes: StringProperty(
        name='Base Color',
        default='BC BaseColor Albedo',
        description='YourTexture"_BC"')
    texture_suffixes: StringProperty(
        name='Subsurface Color',
        default='T',
        description='"T_"YourTexture')
    def execute(self, context):
        global texture_pref
        global texture_suf
        tags = context.preferences.addons[__name__].preferences.prefixes_suffixes
        texture_pref = tags.texture_prefixes.split(' ')
        texture_suf = tags.texture_suffixes.split(' ')
# varibles

extension = '.tga'
texture_basecolor_path = ' '
texture_basecolor_name = ' '

# material presets path
rootdir = os.path.dirname(os.path.realpath(__file__))
material_presets_path = rootdir.replace("'\'", "'/'") + "/material_presets.blend\\Material\\"

prefix = "T_"
tex_basecolor_suf = ['_BC', '_Albedo', '_BaseColor']
tex_packed_suf = ['_ORM', '_ARM', '_MRA' '_RMA' '_OMR']
tex_normal_suf = ['_N', '_Normal']

filename_ext = '_BC.tga'
filter_glob: StringProperty(
    default='_BC*.tga',
    # options={'HIDDEN'}
)

class select_texture_file(Operator, ImportHelper):
    bl_idname = 'object.select_file'
    bl_label = 'Select Base Color'
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = '.tga'
    filter_glob: StringProperty(
        default='*_BC.tga',
        options={'HIDDEN'}
    )
    def execute(self, context):
        print('imported file: ', self.filepath)
        global texture_basecolor_path
        global texture_basecolor_name
        global extension
        extension = extension
        texture_basecolor_path = self.filepath
        texture_basecolor_name = os.path.basename(self.filepath)
        global prefix
        suffix = ['_BC', 'ORM', '_N', '.tga']
        texture_basecolor_name = texture_basecolor_name.removeprefix(prefix)
        for i in range(len(suffix)):
            texture_basecolor_name = texture_basecolor_name.removesuffix(suffix[i-1])
        print(texture_basecolor_name)
        return {'FINISHED'}
class SetupMaterialOperator(bpy.types.Operator):
    bl_idname = "object.setup_fast_material_operator"
    bl_label = "Setup Material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        preset_name = "UnrealEnginePreset"

        # Delete preset material before naming
        for material in bpy.data.materials:
            if material.name == preset_name:
                bpy.data.materials.remove(material)
                print(f"Material '{preset_name}' deleted.")
        # Append preset
        global material_presets_path
        bpy.ops.wm.append(filename=preset_name, directory=material_presets_path)
        # Assign material on active object
        mat = bpy.data.materials.get(preset_name)
        obj = context.active_object
        try:
            obj.data.materials[0] = mat
        except:
            bpy.ops.object.material_slot_add()
            obj.data.materials[0] = mat
        # Import texture and give material name as texture name wiout prefix
        global texture_basecolor_path
        global texture_basecolor_name
        global tex_basecolor_suf
        global tex_normal_suf
        global tex_packed_suf
        prefix_fix = '\T_'
        mat.name = "M_" + texture_basecolor_name
        for sufix in tex_basecolor_suf:
            try:
                new_img = bpy.data.images.load(filepath = os.path.dirname(texture_basecolor_path) + prefix_fix + texture_basecolor_name + sufix + extension)
                obj.material_slots[0].material.node_tree.nodes["BaseColor"].image = new_img
            except:
                pass              
        for sufix in tex_packed_suf:
            try:
                new_img = bpy.data.images.load(filepath = os.path.dirname(texture_basecolor_path) + prefix_fix + texture_basecolor_name + sufix + extension)
                obj.material_slots[0].material.node_tree.nodes["PackedTexture"].image = new_img
                try:
                    obj.material_slots[0].material.node_tree.nodes["PackedTexture"].image.colorspace_settings.name='Non-Color'
                except:
                    obj.material_slots[0].material.node_tree.nodes["PackedTexture"].image.colorspace_settings.name='Utility - Raw'
            except:
                pass     
        for sufix in tex_normal_suf:
            try:
                new_img = bpy.data.images.load(filepath = os.path.dirname(texture_basecolor_path) + prefix_fix + texture_basecolor_name + sufix + extension)
                obj.material_slots[0].material.node_tree.nodes["Normal"].image = new_img
                try:
                    obj.material_slots[0].material.node_tree.nodes["Normal"].image.colorspace_settings.name='Non-Color'
                except:
                    obj.material_slots[0].material.node_tree.nodes["Normal"].image.colorspace_settings.name='Utility - Raw'
            except:
                pass                           
        return {'FINISHED'}
class FastMaterialOperator(Operator, ImportHelper):
    bl_idname = "object.fast_material_operator"
    bl_label = "Quick Material"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = '.tga'
    filter_glob: StringProperty(
        default='*_BC.tga',
        options={'HIDDEN'}
    )
    def execute(self, context):
        global texture_basecolor_path
        print('imported file: ', self.filepath)
        global texture_basecolor_name
        texture_basecolor_path = self.filepath
        texture_basecolor_name = os.path.basename(self.filepath)

        prefix = "T_"
        suffix = ['_BC', 'ORM', '_N', '.tga']
        texture_basecolor_name = texture_basecolor_name.removeprefix(prefix)
        for i in range(len(suffix)):
            texture_basecolor_name = texture_basecolor_name.removesuffix(suffix[i-1])
        print(texture_basecolor_name)
        bpy.ops.object.setup_fast_material_operator('INVOKE_DEFAULT') 
        return {'FINISHED'}
class FastMaterialsPanel(bpy.types.Panel):
    bl_label = "Fast Materials"
    bl_idname = "MATERIAL_PT_fastmaterials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FM'

    def draw(self, context):
        layout = self.layout  # Use layout directly, not self.layout
        layout.operator("object.fast_material_operator")
        # layout.operator("object.select_file")
        # layout.operator("object.setup_fast_material_operator")
        obj = context.active_object
        if obj is None:
            return
        
        
        layout.template_list("MATERIAL_UL_matslots","",obj,"material_slots",obj,"active_material_index", rows=4)
        mat = obj.active_material
        
        if mat is None:
            return
        
        group = None
        for node in mat.node_tree.nodes:
            if node.type =='GROUP':
                group = node
                break
        if group is None:
            return

        box = layout.box()
        box.use_property_split=True
        box.use_property_decorate = False
        for input in group.inputs:
            if input.name.startswith("TF"):
                pass
            else:
                box.prop(input,"default_value",text=input.name)



# Settings End
class ExampleAddonPreferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__
    # prefixes_suffixes: bpy.props.PointerProperty(type=FastMaterialsPreferences)
    def draw(self, context):
        # tags = self.prefixes_suffixes
        layout = self.layout
        col = layout.column()

        box = layout.box()
        col = box.column(align=True)

        # col.prop(tags, "base_color")
        # col.prop(tags, "sss_color")

        box = layout.box()
        col = box.column(align=True)


classes = (
    SetupMaterialOperator,
    FastMaterialsPanel,
    FastMaterialOperator,
    select_texture_file,
    ExampleAddonPreferences,
    OBJECT_OT_addon_prefs_example,
    FastMaterialsPreferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

