# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

SPARK_ADDON_TAG = "spark_blender_addon"


def is_context_valid(context):
    return (
        len(context.selected_objects) == 1
        and context.active_object is not None
        and context.active_object.type == "MESH"
    )


class SparkOperatorsMixin(object):
    @classmethod
    def poll(cls, context):
        return is_context_valid(context)

    def tag_from_plugin(self, context):
        context.active_object[SPARK_ADDON_TAG] = 1
