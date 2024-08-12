# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

import bpy
from bpy_extras.io_utils import ExportHelper

from .spark_operators_mixin import SparkOperatorsMixin


class OBJECT_OT_SparkOperator_ExportForSparkAR(
    bpy.types.Operator, SparkOperatorsMixin, ExportHelper
):
    bl_idname = "object.export_for_spark_ar"
    bl_label = "Export Mesh"
    bl_description = "Export optimized mesh"
    bl_options = {"PRESET"}

    # Select export format based on Blender version
    filename_ext = "*.gltf" if bpy.app.version < (4, 0, 0) else "*.glb"

    hide_props_region = True

    HIDDEN = "HIDDEN"

    filter_glob: bpy.props.StringProperty(
        default=filename_ext,
        options={HIDDEN},
        maxlen=255,
    )

    def execute(self, context):
        if bpy.ops.object.spark_decimation.poll():
            bpy.ops.object.spark_decimation()

        self.tag_from_plugin(context)
        self._export_mesh()

        self.report({"INFO"}, "Export complete.")

        return {"FINISHED"}

    def _export_mesh(self):
        bpy.ops.export_scene.gltf(
            # Format
            export_format="GLTF_EMBEDDED" if bpy.app.version < (4, 0, 0) else "GLB",
            filepath=self.filepath,
            check_existing=False,
            # Setup
            export_cameras=False,
            export_lights=False,
            export_yup=True,
            use_selection=True,
            export_extras=True,
            will_save_settings=True,
            # Materials and Textures
            export_texcoords=True,
            export_image_format="AUTO",
            # Mesh Data
            export_normals=True,

            # * Blender 4.2 doesn't support this setting anymore
            # export_colors=True,
            
            # Deformers
            export_skins=True,
            export_morph=True,
            # Animation
            export_animations=True,
            export_force_sampling=False,
        )
