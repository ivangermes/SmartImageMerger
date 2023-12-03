from enum import Enum
from typing import Self
from tempfile import NamedTemporaryFile

import flet as ft

import cv2 as cv
from stitching import AffineStitcher

ALLOWED_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "tif",
    "tiff",
    "JPG",
    "JPEG",
    "PNG",
    "TIF",
    "TIFF",
]


# TODO:
# - [x] add disable button on process
# - [x] add preloader
# - [x] add input images preview
# - [x] add output images preview
# - [x] delete in files
# - [x] make states
# - [ ] styling
# - [x] refactoring
# - [ ] type cheickng
# - [ ] add comments
# - [ ] make async (?)
# - [ ] exception and error handling
# - [ ] add icon
# - [ ] check that windows clear TMP files
# - [ ] add russian language
# - [ ] building for linux and windows


class DeletableImage(ft.UserControl):
    def __init__(self, file_path, delete_image):
        super().__init__()

        self.file_path = file_path

        self.delete_image = delete_image

    def build(self):
        return ft.Stack(
            [
                ft.Container(
                    # expand=True,
                    # image_fit=ft.ImageFit.SCALE_DOWN,
                    # alignment=ft.alignment.top_right,
                    content=ft.Image(
                        # expand=True,
                        src=self.file_path,
                        fit=ft.ImageFit.SCALE_DOWN,
                        # width=200,
                        # height=200
                    ),
                    bgcolor="#666666",
                    border_radius=ft.border_radius.all(5),
                    # padding=ft.padding.only(
                    #     left=10, right=10, top=40, bottom=10
                    # ),
                    border=ft.border.all(1, ft.colors.BLACK),
                ),
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.icons.CLOSE,
                        icon_color="gray",
                        icon_size=20,
                        tooltip="Remove image",
                        on_click=self.remove_clicked,
                    ),
                    alignment=ft.alignment.top_right,
                ),
            ],
            # width=220,
            # height=220,
            expand=True,
        )

    def get_path(self):
        return self.file_path

    def remove_clicked(self, e):
        self.delete_image(self)


class StitchApp(ft.UserControl):
    def __init__(self, *args, **kargs):
        self.parent_page = kargs["page"]
        del kargs["page"]

        super().__init__(*args, **kargs)

        self.panorama = None

    def build(self):
        self.states = Enum(
            "states", ["START", "READY", "NOT_READY", "WORKING", "DONE"]
        )

        self.stitching_images = ft.Ref[ft.GridView]()
        self.add_image_button = ft.Ref[ft.ElevatedButton]()
        self.process_button = ft.Ref[ft.ElevatedButton]()

        self.preloader = ft.Ref[ft.ProgressRing]()
        self.result_image_container = ft.Ref[ft.Container]()
        self.result_image = ft.Ref[ft.Image]()
        self.save_result_image_button = ft.Ref[ft.ElevatedButton]()

        self.file_picker = ft.FilePicker(on_result=self.on_pick_files_dialog)
        self.file_saver = ft.FilePicker(on_result=self.on_save_dialog)
        self.parent_page.overlay.append(self.file_picker)
        self.parent_page.overlay.append(self.file_saver)

        left_column = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            controls=[
                ft.GridView(
                    ref=self.stitching_images,
                    expand=True,
                    runs_count=2,
                    max_extent=400,
                    child_aspect_ratio=1.0,
                    spacing=5,
                    run_spacing=5,
                    auto_scroll=True,
                ),
                ft.ElevatedButton(
                    ref=self.add_image_button,
                    text="Add images",
                    icon="ADD_PHOTO_ALTERNATE_OUTLINED",
                    on_click=lambda _: self.file_picker.pick_files(
                        allow_multiple=True,
                        dialog_title="Select images",
                        allowed_extensions=ALLOWED_EXTENSIONS,
                    ),
                ),
                ft.ElevatedButton(
                    ref=self.process_button,
                    text="Stitch",
                    icon="JOIN_FULL",
                    height=50,
                    width=150,
                    disabled=True,
                    on_click=self.on_process_button,
                ),
            ],
        )

        right_column = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.ProgressRing(
                    ref=self.preloader,
                    width=32,
                    height=32,
                    stroke_width=4,
                    visible=False,
                ),
                ft.Container(
                    expand=True,
                    content=ft.Container(
                        ref=self.result_image_container,
                        content=ft.Image(
                            ref=self.result_image,
                            src="",
                        ),
                        bgcolor="#666666",
                        padding=10,
                        border=ft.border.all(1, ft.colors.BLACK),
                        visible=False,
                    ),
                ),
                ft.ElevatedButton(
                    ref=self.save_result_image_button,
                    visible=False,
                    text="Save image",
                    icon="FILE_DOWNLOAD_OUTLINED",
                    on_click=lambda _: self.file_saver.save_file(
                        dialog_title="Save images",
                        allowed_extensions=ALLOWED_EXTENSIONS,
                    ),
                ),
            ],
        )

        return [
            ft.Row(
                expand=True,
                controls=[
                    left_column,
                    ft.VerticalDivider(),
                    right_column,
                ],
            )
        ]

    def set_state(self, state):  # TODO: add self.states
        match state:
            case self.states.START:
                self.process_button.current.disabled = True
                self.preloader.current.visible = False
                self.result_image_container.current.visible = False
                self.save_result_image_button.current.visible = False

            case self.states.READY:
                self.process_button.current.disabled = False

            case self.states.NOT_READY:
                self.process_button.current.disabled = True

            case self.states.WORKING:
                self.process_button.current.disabled = True
                self.preloader.current.visible = True
                self.result_image_container.current.visible = False
                self.save_result_image_button.current.visible = False

            case self.states.DONE:
                self.process_button.current.disabled = False
                self.preloader.current.visible = False
                self.result_image_container.current.visible = True
                self.save_result_image_button.current.visible = True

        self.update()

    def stitching_image_delete(self, im):
        self.stitching_images.current.controls.remove(im)
        self.update()

        if len(self.stitching_images.current.controls) > 1:
            self.set_state(self.states.READY)
        else:
            self.set_state(self.states.NOT_READY)

    def on_pick_files_dialog(self, e: ft.FilePickerResultEvent):
        for file in e.files:
            im = DeletableImage(file.path, self.stitching_image_delete)
            self.stitching_images.current.controls.append(im)

        if len(self.stitching_images.current.controls) > 1:
            self.set_state(self.states.READY)
        else:
            self.set_state(self.states.NOT_READY)

    def on_process_button(self, e):
        self.set_state(self.states.WORKING)

        stitcher = AffineStitcher()

        ims_paths = [
            im_path.get_path()
            for im_path in self.stitching_images.current.controls
        ]

        self.panorama = stitcher.stitch(ims_paths)

        result_image_tmp_file = NamedTemporaryFile(delete=False, suffix=".png")
        cv.imwrite(result_image_tmp_file.name, self.panorama)

        self.result_image.current.src = result_image_tmp_file.name
        self.update()

        self.set_state(self.states.DONE)

    def on_save_dialog(self, e: ft.FilePickerResultEvent):
        if e.path:
            cv.imwrite(e.path, self.panorama)


def main(page: ft.Page):
    page.title = "Image Stitcher"

    page.window_min_width = 360
    page.window_min_height = 800

    page.padding = 20
    page.theme_mode = ft.ThemeMode.DARK

    page.add(StitchApp(expand=True, page=page))


# import logging
# logging.basicConfig(level=logging.DEBUG)


ft.app(target=main)
