# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

import bpy

from .spark_operators_mixin import is_context_valid, SparkOperatorsMixin


def get_unit_scale(unit):
    """Conversion from meters."""
    if unit == "cm":
        return 100
    if unit == "in":
        return 39.370079
    if unit == "ft":
        return 3.28084


def get_current_height_in_selected_unit(context):
    if not is_context_valid(context):
        return (0, 0, 0)
    else:
        unit = context.screen.sparkar_scale.resizeUnit
        return context.active_object.dimensions * get_unit_scale(unit)


def should_height_setting_be_updated(context, eps=0.0001):
    current_height = get_current_height_in_selected_unit(context)[2]
    return abs(context.screen.sparkar_scale.height - current_height) > eps


def update_sparkar_scale_settings(context):
    if should_height_setting_be_updated(context):
        dims = get_current_height_in_selected_unit(context)
        resize_settings = context.screen.sparkar_scale
        (resize_settings.depth, resize_settings.width, resize_settings.height) = dims


def resize_active_model(self, context):
    if not should_height_setting_be_updated(bpy.context):
        return
    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    override = {
                        "area": area,
                        "region": region,
                        "edit_object": context.edit_object,
                    }
                    bpy.ops.object.spark_resize(override)


class SparkARToolkitScaleSettings(bpy.types.PropertyGroup):
    UNIT = "Unit"
    CM = "cm"
    IN = "in"
    FT = "ft"
    WIDTH_LABEL = "Width"
    DEPTH_LABEL = "Depth"
    ADJUST_LABEL = "Adjust height"
    EMPTY_LABEL = ""

    resizeUnit: bpy.props.EnumProperty(
        name=UNIT,
        items=[
            (CM, CM, EMPTY_LABEL, 1),
            (IN, IN, EMPTY_LABEL, 2),
            (FT, FT, EMPTY_LABEL, 3),
        ],
        description=UNIT,
        default=CM,
    )
    height: bpy.props.FloatProperty(
        name=ADJUST_LABEL,
        update=resize_active_model,
        default=0,
        precision=2,
        min=0,
    )
    width: bpy.props.FloatProperty(name=WIDTH_LABEL, default=0, min=0, precision=2)
    depth: bpy.props.FloatProperty(name=DEPTH_LABEL, default=0, min=0, precision=2)


class OBJECT_OT_SparkOperator_Resize(bpy.types.Operator, SparkOperatorsMixin):
    bl_idname = "object.spark_resize"
    bl_label = "Resize"
    bl_description = "Resize"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        current_height = context.active_object.dimensions[2]
        settings = context.screen.sparkar_scale
        expected_height = settings.height
        expected_unit = settings.resizeUnit
        unit_scale = get_unit_scale(expected_unit)

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        scale = expected_height / (unit_scale * current_height)
        if scale > 0:
            bpy.ops.transform.resize(value=(scale, scale, scale))
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.object.location_clear()
        return {"FINISHED"}
