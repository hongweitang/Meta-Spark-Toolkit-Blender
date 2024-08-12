# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

import bpy

from .spark_operators_mixin import SparkOperatorsMixin


class OBJECT_OT_SparkOperator_PivotCenter(bpy.types.Operator, SparkOperatorsMixin):
    bl_idname = "object.spark_pivot_center"
    bl_label = "Set pivot point to center"
    bl_description = "Set pivot point to center"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_VOLUME", center="MEDIAN")
        bpy.ops.object.location_clear()
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        return {"FINISHED"}


class OBJECT_OT_SparkOperator_PivotBottom(bpy.types.Operator, SparkOperatorsMixin):
    bl_idname = "object.spark_pivot_bottom"
    bl_label = "Set pivot point to bottom"
    bl_description = "Set pivot point to bottom"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        mesh_base = context.active_object.bound_box

        bottom_pivot = [0, 0, 0]
        bottom_pivot[0] = (mesh_base[0][0] + mesh_base[7][0]) / 2
        bottom_pivot[1] = (mesh_base[0][1] + mesh_base[7][1]) / 2
        bottom_pivot[2] = (mesh_base[0][2] + mesh_base[7][2]) / 2

        context.scene.cursor.location = bottom_pivot
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        bpy.ops.object.location_clear()
        context.scene.cursor.location = (0, 0, 0)
        return {"FINISHED"}
