bl_info = {
    "name": "Quick Material Setup",
    "blender": (3, 6, 0),
    "category": "Material",
    "location": "Properties > Material",
    "description": "Quickly import textures as materials",
    "author": "Nucky3d",
    "version": (1, 2),
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/nucky3d/Quick-Material-Setup-",
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
class ExampleAddonPreferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__
    # prefixes_suffixes: bpy.props.PointerProperty(type=FastMaterialsPreferences)

    prefix: bpy.props.StringProperty(
    default="T_", 
    description='"T_"YourTexture'
    )
    presets_p: bpy.props.StringProperty(
    default="UnrealEnginePreset_ORM UnrealEnginePreset_RMA", 
    description='"T_"YourTexture'
    )

    sufix_bc: bpy.props.StringProperty(
    default="_BC  _BaseColor _Albedo",
    description='YourTexture"_BC"' 
    )
    sufix_pack: bpy.props.StringProperty(
    default="_ORM  _RMA",
    )
    sufix_n: bpy.props.StringProperty(
    default="_N  _Normal",
    )
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        # row.prop(self, "presets_p", text="List of preset from blend file")
        # row = layout.row()
        row.prop(self, "prefix", text="Prefix for textures")
        row = layout.row()
        row.prop(self, "sufix_bc", text="Sufix for color textures")
        row = layout.row()
        row.prop(self, "sufix_pack", text="Sufix for packed textures")
        row = layout.row()
        row.prop(self, "sufix_n", text="Sufix for normal textures")
        row.separator()

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
texture_basecolor_path = ' '
texture_basecolor_name = ' '
preset_name = "UnrealEnginePreset_ORM"
preset_display_name = 'UE ORM'
# material presets path
rootdir = os.path.dirname(os.path.realpath(__file__))
material_presets_path = rootdir.replace("'\'", "'/'") + "/material_presets.blend\\Material\\"

class SetupMaterialOperator(bpy.types.Operator):
    bl_idname = "object.setup_fast_material_operator"
    bl_label = "Setup Material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # vars from preferences
        global preset_name
        tex_basecolor_suf = (context.preferences.addons[__name__].preferences.sufix_bc).split()
        tex_packed_suf = (context.preferences.addons[__name__].preferences.sufix_pack).split()
        tex_normal_suf = (context.preferences.addons[__name__].preferences.sufix_n).split()
        prefix = (context.preferences.addons[__name__].preferences.prefix)
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
        prefix_fix = '\\' + prefix
        mat.name = "M_" + texture_basecolor_name
        exstensions = ['.tga', '.png', '.jpg', '.tif', '.tiff', '.exr']
        for i in range(len(exstensions)):
                if exstensions[i] in texture_basecolor_path:
                    extension = exstensions[i]
                else:
                    pass
        for sufix in tex_basecolor_suf:
            try:
                new_img = bpy.data.images.load(filepath = os.path.dirname(texture_basecolor_path) + prefix_fix + texture_basecolor_name + sufix + extension)
                obj.material_slots[0].material.node_tree.nodes["BaseColor"].image = new_img
            except:
                # print(os.path.dirname(texture_basecolor_path) + prefix_fix + texture_basecolor_name + sufix + extension)
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
                # print(os.path.dirname(texture_basecolor_path) + prefix_fix + texture_basecolor_name + sufix + extension)
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
                # print(os.path.dirname(texture_basecolor_path) + prefix_fix + texture_basecolor_name + sufix + extension)
                pass                           
        return {'FINISHED'}
    


class FastMaterialOperator(Operator, ImportHelper):
    bl_idname = "object.fast_material_operator"
    bl_label = "Quick Material"
    bl_options = {'REGISTER', 'UNDO'}

    # filename_ext = '.tga'
    filter_glob: StringProperty(
        default='*_BC*',
        # options={'HIDDEN'}
    )
    def execute(self, context):
        global texture_basecolor_path
        global texture_basecolor_name
        prefix = (context.preferences.addons[__name__].preferences.prefix)
        tex_basecolor_suf = (context.preferences.addons[__name__].preferences.sufix_bc).split()
        
        print('imported file: ', self.filepath)
        texture_basecolor_path = self.filepath
        texture_basecolor_name = bpy.path.basename(self.filepath)

        suffix = ['.tga', '.png', '.jpg', '.tif', '.tiff', '.exr'] + tex_basecolor_suf
        texture_basecolor_name = texture_basecolor_name.removeprefix(prefix)
        for i in range(len(suffix)):
            texture_basecolor_name = texture_basecolor_name.removesuffix(suffix[i-1])
        print(texture_basecolor_name)
        bpy.ops.object.setup_fast_material_operator('INVOKE_DEFAULT') 
        return {'FINISHED'}
    



class MT_Preset_UE_ORM(bpy.types.Operator):
    bl_idname = "object.preset_ue_orm"
    bl_label = "UE ORM"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        global preset_name
        presets = (context.preferences.addons[__name__].preferences.presets_p).split()
        preset_name = presets[0]
        global preset_display_name
        preset_display_name = 'UE ORM'
        return {'FINISHED'}
class MT_Preset_UE_RMA(bpy.types.Operator):
    bl_idname = "object.preset_ue_rma"
    bl_label = "UE RMA"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        global preset_name
        presets = (context.preferences.addons[__name__].preferences.presets_p).split()
        preset_name = presets[1]
        global preset_display_name
        preset_display_name = 'UE RMA'
        return {'FINISHED'}

class MT_PresetsMenu(bpy.types.Menu):
    global preset_display_name
    bl_label = "Presets"
    bl_idname = "view3D.presets_menu"

    # Drawing a nested menu with three operators(buttons)
    def draw(self, context):
        layout = self.layout 
        layout.operator('object.preset_ue_orm')
        layout.operator('object.preset_ue_rma')
        


class FastMaterialsPanel(bpy.types.Panel):
    bl_label = "Fast Materials"
    bl_idname = "MATERIAL_PT_fastmaterials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QMS'

    def draw(self, context):
        # global preset_name
        # presets = (context.preferences.addons[__name__].preferences.presets_p).split()
        # preset_name = presets[0]
        layout = self.layout  # Use layout directly, not self.layout
        layout.operator("object.fast_material_operator")
        layout.menu('view3D.presets_menu', text=preset_display_name)
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


classes = (
    SetupMaterialOperator,
    FastMaterialsPanel,
    FastMaterialOperator,
    ExampleAddonPreferences,
    FastMaterialsPreferences,
    MT_Preset_UE_ORM,
    MT_PresetsMenu,
    MT_Preset_UE_RMA,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

