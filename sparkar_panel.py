# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

import bmesh
import bpy

from .spark_operators_export import OBJECT_OT_SparkOperator_ExportForSparkAR
from .spark_operators_mixin import is_context_valid
from .spark_operators_optimization import (
    OBJECT_OT_SparkOperator_Decimation,
    OBJECT_OT_SparkOperator_MeshCleanUp,
)
from .spark_operators_pivot import (
    OBJECT_OT_SparkOperator_PivotBottom,
    OBJECT_OT_SparkOperator_PivotCenter,
)
from .spark_operators_scale import get_unit_scale
from .sparkar_panel_base import SparkARPanelBase


class PANEL0_PT_SparkAR_Panel(bpy.types.Panel, SparkARPanelBase):
    bl_idname = "PANEL0_PT_SparkAR_Panel"
    bl_label = "Meta Spark Toolkit"
    bl_category = "Meta Spark Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    TRIS_COUNT_ERROR = 50000
    TRIS_COUNT_WARNING = 30000
    HEIGHT_MIN = 0.01  # unit: meters
    HEIGHT_MAX = 5  # unit: meters
    GUIDELINES_LINK = "https://sparkar.facebook.com/ar-studio/learn/documentation/technical-guidelines"

    tri_count = 0

    # ASSET SELECTION SECTION

    def _draw_asset_selection_box(self, context, layout):
        if len(context.selected_objects) > 1:
            text = [
                "Selecting multiple meshes is not supported.",
                "Please select a single mesh.",
            ]
            layout.alert = True
            layout.scale_y = 0.5
        elif not is_context_valid(context):
            text = ["Select a mesh to get started."]
        else:
            text = ["Name: " + context.active_object.name]
        for line in text:
            layout.label(text=line)

    # OPTIMIZATION SECTION

    def _icon_and_description_for_tri_count(self, context, count):
        if not is_context_valid(context):
            icon = "NONE"
            message_lines = ["Triangle count must meet the technical requirements."]
        elif count < self.TRIS_COUNT_WARNING:
            icon = self.OK_ICON
            message_lines = ["Triangle count meets requirements."]
        elif count < self.TRIS_COUNT_ERROR:
            icon = self.WARNING_ICON
            message_lines = ["Reduce triangle count to improve performance."]
        else:
            icon = self.ERROR_ICON
            message_lines = [
                "Triangle count doesn't meet requirements.",
                "Reduce to export your mesh.",
            ]
        return icon, message_lines

    def _draw_tri_count_summary(self, context, layout):
        if not is_context_valid(context):
            self.tri_count = 0
        else:
            bm = bmesh.new()
            bm.from_object(context.active_object, context.evaluated_depsgraph_get())
            self.tri_count = len(bm.calc_loop_triangles())

        label = "Triangles: " + self._pretty_print_count(self.tri_count)
        icon_alert = self.tri_count >= self.TRIS_COUNT_ERROR
        icon, message_lines = self._icon_and_description_for_tri_count(
            context, self.tri_count
        )

        self._draw_label_with_status_icon_and_learn_more_section(
            context,
            layout,
            label,
            icon,
            icon_alert,
            message_lines,
            self.GUIDELINES_LINK,
        )

    def _draw_reduce_polygons_section(self, context, layout):
        row = layout.row()
        ratio_button = row.split()
        apply_button = row.split()

        highlight_apply = False
        if bpy.ops.object.spark_decimation.poll():
            optimization_settings = context.active_object.sparkar_optimization
            ratio_button.prop(
                optimization_settings, "InvertedReducePercentage", text=""
            )

            if optimization_settings.InvertedReducePercentage == 0:
                apply_button.enabled = False
            else:
                highlight_apply = True
        else:
            ratio_button.operator(
                OBJECT_OT_SparkOperator_Decimation.bl_idname, text="0%"
            )
            row.enabled = False
        apply_button.operator(
            OBJECT_OT_SparkOperator_Decimation.bl_idname,
            text="Apply",
            depress=highlight_apply,
        )

    def _draw_mesh_opt_box(self, context, layout):
        summary = layout.box()
        self._draw_tri_count_summary(context, summary)

        layout.label(text="Reduce Triangles")
        decimation_row = layout.row()
        decimation_row.separator(factor=0.0)
        self._draw_reduce_polygons_section(context, decimation_row)
        decimation_row.separator(factor=0.0)

        layout.label(text="Clean Up Mesh")
        cleanup_row = layout.row()
        cleanup_row.separator(factor=0.0)
        cleanup_row.operator(
            OBJECT_OT_SparkOperator_MeshCleanUp.bl_idname, text="Apply"
        )
        cleanup_row.separator(factor=0.0)
        layout.separator(factor=0.0)

    # SCALE AND POSITIONING SECTION
    def _draw_size_summary_box(self, context, layout):
        unit = context.screen.sparkar_scale.resizeUnit
        if is_context_valid(context):
            dims = context.active_object.dimensions * get_unit_scale(unit)
        else:
            dims = (0, 0, 0)

        current_height = str(round(dims[2], 2))
        resize_settings = context.screen.sparkar_scale
        height_label = "Height: {}{}".format(current_height, resize_settings.resizeUnit)

        if not is_context_valid(context):
            text = ["Height should follow the technical guidelines."]
            icon = "NONE"
        else:
            heightM = context.active_object.dimensions[2]
            if heightM > self.HEIGHT_MAX:
                text = ["Decrease height for better control in Meta Spark Studio."]
                icon = self.WARNING_ICON
            elif heightM < self.HEIGHT_MIN:
                text = ["Increase height for better control in Meta Spark Studio."]
                icon = self.WARNING_ICON
            else:
                text = ["Height follows guidelines."]
                icon = self.OK_ICON

        self._draw_label_with_status_icon_and_learn_more_section(
            context, layout, height_label, icon, False, text, self.GUIDELINES_LINK
        )

    def _draw_scale_section(self, context, layout):
        labels_row = layout.row(align=True)
        labels_row.enabled = False
        labels_row.scale_y = 0.5
        labels_row.separator(factor=0.0)
        labels_row.label(text="Height")
        labels_row.label(text="Width")
        labels_row.label(text="Depth")
        labels_row.label(text="")
        labels_row.separator(factor=0.0)

        resize_settings = context.screen.sparkar_scale
        height_row = layout.row()
        height_row.separator(factor=0.0)
        if not bpy.ops.object.spark_resize.poll():
            height_row.enabled = False

        height_field = height_row.split()
        height_field.prop(resize_settings, "height", text="")
        width_field = height_row.split()
        width_field.enabled = False
        width_field.label(text=str(round(resize_settings.width, 2)))
        depth_field = height_row.split()
        depth_field.enabled = False
        depth_field.label(text=str(round(resize_settings.depth, 2)))

        height_row.prop(resize_settings, "resizeUnit", text="")
        height_row.separator(factor=0.0)

    def _draw_positioning_scaling_box(self, context, layout):
        summary_box = layout.box()
        self._draw_size_summary_box(context, summary_box)

        layout.label(text="Scale")
        self._draw_scale_section(context, layout)

        layout.label(text="Pivot Point")
        pivot_row = layout.row()
        pivot_row.separator(factor=0.0)
        pivot_row.operator(OBJECT_OT_SparkOperator_PivotCenter.bl_idname, text="Center")
        pivot_row.operator(OBJECT_OT_SparkOperator_PivotBottom.bl_idname, text="Bottom")
        pivot_row.separator(factor=0.0)
        layout.separator(factor=0.0)

    # EXPORT

    def _is_export_disabled(self, context):
        if len(context.selected_objects) == 0:
            return True
        return self.tri_count >= self.TRIS_COUNT_ERROR

    def draw_export(self, context, layout):
        export_description = ["Export your optimized mesh from Meta Spark Toolkit."]
        layout.separator(factor=0.0)
        for line in export_description:
            row = layout.row()
            row.scale_y = 0.5
            row.enabled = False
            row.label(text=line)
        button = layout.row()
        button.scale_y = 1.5
        button.operator(
            OBJECT_OT_SparkOperator_ExportForSparkAR.bl_idname,
            text="Export Mesh",
            depress=True,
        )
        if self._is_export_disabled(context):
            button.enabled = False

    # PANEL

    def draw_header(self, context):
        self.layout.label(text="", icon="TOOL_SETTINGS")

    def draw(self, context):
        self.layout.label(text="Mesh", icon="FILE_3D")
        asset_selection_box = self.layout.box()
        self._draw_asset_selection_box(context, asset_selection_box)

        self.layout.label(text="Optimization", icon="SHADERFX")
        mesh_optimisation_box = self.layout.box()
        self._draw_mesh_opt_box(context, mesh_optimisation_box)

        self.layout.label(text="Scale and Positioning", icon="PIVOT_BOUNDBOX")
        pivot_and_scaling_box = self.layout.box()
        self._draw_positioning_scaling_box(context, pivot_and_scaling_box)

        self.layout.label(text="Export", icon="EXPORT")
        export_box = self.layout.box()
        self.draw_export(context, export_box)
