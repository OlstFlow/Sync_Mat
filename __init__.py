# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import bpy

bl_info = {
    "name": "Sync Mat",
    "author": "Olst, GPT",
    "version": (1, 1, 4),
    "blender": (4, 3, 0),
    "location": "Material > Surface > Default Value (Context Menu)", # Updated location description
    "description": "Sync Base Color and Alpha to Viewport Display color",
    "category": "Material",
}

# Helper function to handle object selection logic based on modifier keys
def _execute_on_objects(context, event, sync_function_single, sync_function_multiple):
    """
    Determines the target objects (active, selected, or all) based on
    Shift/Ctrl key presses and executes the provided sync functions.

    :param context: Blender context.
    :param event: The event that triggered the operator (contains key states).
    :param sync_function_single: Function to call for the active object's active material.
    :param sync_function_multiple: Function to call for each material on an object (used for selected/all).
    """
    sync_all = event.ctrl and not event.shift # Prioritize Ctrl over Shift+Ctrl
    sync_selected = event.shift and not event.ctrl # Prioritize Shift over Shift+Ctrl

    if sync_all:
        for obj in bpy.data.objects:
            # Check if the object type supports materials
            if obj.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}:
                sync_function_multiple(obj)
    elif sync_selected:
        for obj in context.selected_objects:
             # Check if the object type supports materials
            if obj.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}:
                sync_function_multiple(obj)
    else: # No modifier or both Ctrl+Shift (treat as default)
        obj = context.object
        if obj: # Ensure there is an active object
             # Check if the object type supports materials
            if obj.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}:
                sync_function_single(obj)

class MATERIAL_OT_sync_viewport_display(bpy.types.Operator):
    """Sync Base Color with Viewport Display"""
    bl_idname = "material.sync_viewport_display"
    bl_label = "Sync Base Color to Viewport Display"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = ("Click - to sync current material.\n"
                      "Shift + Click - for selected objects.\n"
                      "Ctrl + Click - for all objects in scene.")

    def invoke(self, context, event):
        # Use the helper function, passing the specific sync methods for this operator
        _execute_on_objects(context, event, self.sync_active_material, self.sync_materials)
        return {'FINISHED'}

    def sync_active_material(self, obj):
        """Syncs the Base Color for the active material of the given object."""
        if obj.active_material:
            material = obj.active_material
            if material and material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        base_color = node.inputs['Base Color'].default_value
                        current_alpha = material.diffuse_color[3]
                        material.diffuse_color = (base_color[0], base_color[1], base_color[2], current_alpha)
                        break # Found Principled BSDF, move to next material/object

    def sync_materials(self, obj):
        """Syncs the Base Color for all materials of the given object."""
        # The check for obj.type is now handled in _execute_on_objects
        for slot in obj.material_slots:
                material = slot.material
                if material and material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            base_color = node.inputs['Base Color'].default_value
                            current_alpha = material.diffuse_color[3]
                            material.diffuse_color = (base_color[0], base_color[1], base_color[2], current_alpha)
                            break # Found Principled BSDF, move to next material slot

class MATERIAL_OT_sync_viewport_alpha(bpy.types.Operator):
    """Sync Alpha from Principled BSDF node to Viewport Display Alpha"""
    bl_idname = "material.sync_viewport_alpha"
    bl_label = "Sync Alpha to Viewport Display"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = ("Click - to sync current material Alpha.\n"
                      "Shift + Click - for selected objects.\n"
                      "Ctrl + Click - for all objects in scene.")

    def invoke(self, context, event):
         # Use the helper function, passing the specific sync methods for this operator
        _execute_on_objects(context, event, self.sync_active_alpha, self.sync_alpha)
        return {'FINISHED'}

    def sync_active_alpha(self, obj):
        """Syncs the Alpha for the active material of the given object."""
        if obj.active_material:
            material = obj.active_material
            if material and material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        alpha_value = node.inputs['Alpha'].default_value
                        material.diffuse_color[3] = alpha_value
                        break # Found Principled BSDF, move to next material/object

    def sync_alpha(self, obj):
        """Syncs the Alpha for all materials of the given object."""
        # The check for obj.type is now handled in _execute_on_objects
        for slot in obj.material_slots:
                material = slot.material
                if material and material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            alpha_value = node.inputs['Alpha'].default_value
                            material.diffuse_color[3] = alpha_value
                            break # Found Principled BSDF, move to next material slot

def menu_func(self, context):
    # Check if the context is appropriate (e.g., right-clicking on a color property)
    # This basic check might need refinement depending on where exactly it should appear.
    # For now, we assume it's called in the right context based on registration.
    layout = self.layout
    layout.separator()
    layout.operator(MATERIAL_OT_sync_viewport_display.bl_idname, text="Sync Base Color to Viewport Display")
    layout.operator(MATERIAL_OT_sync_viewport_alpha.bl_idname, text="Sync Alpha to Viewport Display")

def register():
    bpy.utils.register_class(MATERIAL_OT_sync_viewport_display)
    bpy.utils.register_class(MATERIAL_OT_sync_viewport_alpha)
    bpy.types.UI_MT_button_context_menu.append(menu_func)

def unregister():
    bpy.utils.unregister_class(MATERIAL_OT_sync_viewport_display)
    bpy.utils.unregister_class(MATERIAL_OT_sync_viewport_alpha)
    bpy.types.UI_MT_button_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
