# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.


class SparkARPanelBase(object):
    OK_ICON = "CHECKMARK"
    WARNING_ICON = "ERROR"
    ERROR_ICON = "ERROR"

    def _pretty_print_count(self, count):
        if count < 1000:
            return str(count)
        return str(round(count / 1000, 1)) + "K"

    def _draw_label_with_status_icon_and_learn_more_section(
        self, context, layout, label, icon, alert, description_lines, link
    ):
        row = layout.row()
        if alert:
            row.alert = True
        label_split = row.split()
        label_split.label(text=label)

        icon_split = row.split()
        icon_split.label(text="", icon=icon)

        self._draw_description_with_learn_more(context, layout, description_lines, link)
        layout.separator(factor=0.0)

    def _draw_description_with_learn_more(self, context, layout, lines, link):
        for index in range(len(lines)):
            text = lines[index]

            if index != len(lines) - 1:
                row = layout.row()
                row.scale_y = 0.5
                row.alignment = "LEFT"
                row.enabled = False
                row.label(text=text)
            else:
                row = layout.row(align=True)
                row.alignment = "LEFT"
                text_split = row.split(align=True)
                text_split.scale_y = 0.5
                text_split.alignment = "LEFT"
                text_split.enabled = False
                text_split.label(text=text)
                link_split = row.split(align=True)
                link_split.alignment = "LEFT"
                link_split.scale_y = 0.5
                learn_op = link_split.operator(
                    "wm.url_open", text="Learn More", emboss=False
                )
                learn_op.url = link
