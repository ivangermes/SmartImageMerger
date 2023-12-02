from enum import Enum
from tempfile import NamedTemporaryFile

import flet as ft

import cv2 as cv
from stitching import AffineStitcher

panorama = None

states = Enum("states", ["START", "READY", "NOT_READY", "WORKING", "DONE"])


ALLOWED_EXTENSIONS = [
    "jpg", "jpeg",  "png", "tif", "tiff",
    "JPG", "JPEG",  "PNG", "TIF", "TIFF"
]


# TODO:
# - [x] add disable button on process
# - [x] add preloader
# - [x] add input images preview
# - [x] add output images preview
# - [x] delete in files
# - [ ] make states
# - [ ] styling
# - [ ] refactoring
# - [ ] exception and error handling
# - [ ] add icon
# - [ ] check that windows clear TMP files
# - [ ] add russian language
# - [ ] building for linux and windows



def main(page: ft.Page):
    page.title = "Image Stitcher"
    page.window_min_width = 360  # resizing window limit
    page.window_min_height = 800

    page.horizontal_alignment = "center"
    page.padding = 50

    page.theme_mode = ft.ThemeMode.DARK
    # page.scroll = "auto"
    # page.auto_scroll  = True

    images_grid = ft.Ref[ft.GridView]()
    add_file_button = ft.Ref[ft.ElevatedButton]()
    process_button = ft.Ref[ft.ElevatedButton]()
    save_result_button = ft.Ref[ft.ElevatedButton]()
    preloader = ft.Ref[ft.ProgressRing]()
    file_picker = ft.Ref[ft.FilePicker]()
    result_image_container = ft.Ref[ft.Container]()
    result_image = ft.Ref[ft.Image]()
    file_saver = ft.Ref[ft.FilePicker]()




    def set_state(state: states):
        match state:
            case states.START:
                process_button.current.disabled = True
                preloader.current.visible = False
                result_image_container.current.visible = False
                save_result_button.current.visible = False

            case states.READY:
                process_button.current.disabled = False

            case states.NOT_READY:
                process_button.current.disabled = True

            case states.WORKING:
                process_button.current.disabled = True
                preloader.current.visible = True
                result_image_container.current.visible = False
                save_result_button.current.visible = False
         
            case states.DONE:
                process_button.current.disabled = False
                preloader.current.visible = False
                result_image_container.current.visible = True
                save_result_button.current.visible = True

        page.update()

    class ImageIn(ft.UserControl):
        def __init__(self, file_path):
            super().__init__()
            self.file_path = file_path

        def build(self):
            view = ft.Stack(
                [
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.top_right,
                        content=ft.Image(
                            src=self.file_path,
                            fit=ft.ImageFit.CONTAIN,
                            # width=200,
                            # height=200
                        ),
                        bgcolor="#666666",
                        border_radius=ft.border_radius.all(5),
                        padding=ft.padding.only(
                            left=10,
                            right=10,
                            top=40,
                            bottom=10
                        ),
                        border=ft.border.all(1, ft.colors.BLACK)
                    ),
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.icons.CLOSE,
                            icon_color="gray",
                            icon_size=20,
                            tooltip="Remove image",
                            on_click=self.remove_clicked
                        ),
                        alignment=ft.alignment.top_right,
                    ),
                ],
                # width=220,
                # height=220,
                expand=True,
            )

            return view  

        def get_path(self):
            return self.file_path

        def remove_clicked(self, e ):
            in_image_delete(self)

    def in_image_delete(im):
        images_grid.current.controls.remove(im)
        page.update()

        if len(images_grid.current.controls) > 1:
            set_state(states.READY)
        else:
            set_state(states.NOT_READY)

    def on_pick_files(e: ft.FilePickerResultEvent):
        for file in e.files:
            im = ImageIn(file.path)
            images_grid.current.controls.append(im)

        if len(images_grid.current.controls) > 1:
            set_state(states.READY)
        else:
            set_state(states.NOT_READY)

    def on_process_button(e):
        set_state(states.WORKING)

        stitcher = AffineStitcher()
        global panorama
        images_to_stich = [im_path.get_path() for im_path in images_grid.current.controls]
        print(images_to_stich)
        panorama = stitcher.stitch(images_to_stich)

        result_tmp_file = NamedTemporaryFile(
            delete=False,
            suffix=".png"
        )
        print(result_tmp_file.name)

        cv.imwrite(result_tmp_file.name, panorama)
        result_image.current.src = result_tmp_file.name

        page.update()

        set_state(states.DONE)

    def on_save_result(e: ft.FilePickerResultEvent):
        global panorama
        if e.path:
            cv.imwrite(e.path, panorama)

    file_picker = ft.FilePicker(ref=file_picker, on_result=on_pick_files)
    file_saver = ft.FilePicker(ref=file_saver, on_result=on_save_result)
    page.overlay.append(file_picker)
    page.overlay.append(file_saver)

    left_column = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
        controls=[
            ft.GridView(
                ref=images_grid,
                expand=True,
                runs_count=2,
                # max_extent=400,
                child_aspect_ratio=1.0,
                spacing=5,
                run_spacing=5,
                # auto_scroll=True,
            ),
            ft.ElevatedButton(
                ref=add_file_button,
                text="Add images",
                icon="ADD_PHOTO_ALTERNATE_OUTLINED",
                on_click=lambda _: file_picker.pick_files(
                    allow_multiple=True,
                    dialog_title="Select images",
                    allowed_extensions=ALLOWED_EXTENSIONS
                )
            ),
            ft.ElevatedButton(
                ref=process_button,
                text="Stitch",
                icon="JOIN_FULL",
                height=50,
                width=150,
                disabled=True,
                on_click=on_process_button
            ),
        ]
    )

    right_column = ft.Column(
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.ProgressRing(
                ref=preloader,
                width=32,
                height=32,
                stroke_width=4,
                visible=False
            ),
            ft.Container(
                expand=True,
                content=ft.Container(
                    ref=result_image_container,
                    content=ft.Image(
                        ref=result_image,
                        src="",
                    ),
                    bgcolor="#666666",
                    padding=10,
                    border=ft.border.all(1, ft.colors.BLACK),
                    visible=False,
                    # ink=True,
                ),
            ),
            ft.ElevatedButton(
                ref=save_result_button,
                visible=False,
                text="Save image",
                icon="FILE_DOWNLOAD_OUTLINED",
                on_click=lambda _: file_saver.save_file(
                    dialog_title="Save images",
                    allowed_extensions=ALLOWED_EXTENSIONS
                ),
            ),
        ]
    )

    page.add(
        ft.Row(
            expand=True,
            controls=[
                left_column,
                ft.VerticalDivider(),
                right_column
            ]
        )
    )

# import logging
# logging.basicConfig(level=logging.DEBUG)


ft.app(target=main)
