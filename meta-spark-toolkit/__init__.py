# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

import bpy
from bpy.app.handlers import persistent

from .spark_operators_export import OBJECT_OT_SparkOperator_ExportForSparkAR
from .spark_operators_optimization import (
    OBJECT_OT_SparkOperator_Decimation,
    OBJECT_OT_SparkOperator_MeshCleanUp,
    SparkARToolkitOptimizationSettings,
    update_sparkar_optimization_settings,
)
from .spark_operators_pivot import (
    OBJECT_OT_SparkOperator_PivotBottom,
    OBJECT_OT_SparkOperator_PivotCenter,
)
from .spark_operators_scale import (
    OBJECT_OT_SparkOperator_Resize,
    SparkARToolkitScaleSettings,
    update_sparkar_scale_settings,
)
from .sparkar_panel import PANEL0_PT_SparkAR_Panel

bl_info = {
    "name": "Meta Spark Toolkit",
    "author": "Meta Platforms, Inc.",
    "description": "Meta Spark Toolkit",
    "blender": (4, 2, 0),
    "version": (1, 3, 1),
    "location": "View3D",
    "warning": "",
    "category": "Import-Export",
    "wiki_url": "https://sparkar.facebook.com/ar-studio/learn/articles/creating-and-prepping-assets/toolkit-for-blender#installing-Spark-AR-toolkit",
    "tracker_url": "https://developer.blender.org/maniphest/task/edit/form/2/",
}

classes = (
    SparkARToolkitScaleSettings,
    SparkARToolkitOptimizationSettings,
    OBJECT_OT_SparkOperator_Decimation,
    OBJECT_OT_SparkOperator_MeshCleanUp,
    OBJECT_OT_SparkOperator_Resize,
    OBJECT_OT_SparkOperator_PivotCenter,
    OBJECT_OT_SparkOperator_PivotBottom,
    OBJECT_OT_SparkOperator_ExportForSparkAR,
    PANEL0_PT_SparkAR_Panel,
)


@persistent
def load_handler(scene):
    update_sparkar_optimization_settings(bpy.context)
    update_sparkar_scale_settings(bpy.context)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Screen.sparkar_scale = bpy.props.PointerProperty(
        type=SparkARToolkitScaleSettings
    )
    bpy.types.Object.sparkar_optimization = bpy.props.PointerProperty(
        type=SparkARToolkitOptimizationSettings
    )
    bpy.app.handlers.depsgraph_update_post.append(load_handler)
    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.depsgraph_update_post.remove(load_handler)
    del bpy.types.Object.sparkar_optimization
    del bpy.types.Screen.sparkar_scale
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
