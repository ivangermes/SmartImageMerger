from enum import Enum
import os
from pathlib import Path, PurePath
from tempfile import NamedTemporaryFile
from typing import Any, Callable

import flet as ft

import PIL
from PIL import Image 
import cv2 as cv
import numpy
from stitching import AffineStitcher
from stitching.stitching_error import StitchingError  # StitchingWarning

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

SUPPORTED_IMAGES_FORMATS = ['JPEG', 'PNG', 'TIFF']


WELCOME_TEXT = """
Add two or more images to be merged together.
In any order.

Best for scanned images, not suitable for panorama photos.
"""

def cv_load_image(img_path: str):
    # cv.imread() has error with unicode paths on windows platform
    # https://github.com/opencv/opencv/issues/18305
    # so, we use a workaround
    img = cv.imdecode(
        numpy.fromfile(img_path, dtype=numpy.uint8),
        cv.IMREAD_UNCHANGED,
    )
    if img is None:
        raise MergerError("Bad image " + img_path)

    return img

def cv_save_image(img: numpy.ndarray, img_path: str):
    # cv.imwrite() has error with unicode paths on windows platform
    # https://github.com/opencv/opencv/issues/18305
    # so, we use a workaround
    suffix = str(Path(img_path).suffix)
    is_success, im_buf_arr = cv.imencode(suffix, img)
    if not is_success:
        raise MergerError("Cannot write image " + img_path)
    im_buf_arr.tofile(img_path)

def humanize_exceptions(er):
    """
    Return human redeable error text
    """

    if str(er).startswith("No match exceeds"):
        error_text = (
            "The images could not be merged.\n"
            "Maybe they are too different or have no overlap."
        )
    elif "could not find a writer for the specified extension" in str(er):
        error_text = (
            "Cannot write image. Wrong file type.\n"
            "\n"
            "Specify the correct extension for the image.\n"
            "For example: png or jpeg"
        )
    elif "could not find encoder for the specified extension" in str(er):
        error_text = (
            "Cannot write image. Wrong file type.\n"
            "\n"
            "Specify the correct extension for the image.\n"
            "For example: png or jpeg"
        )
    elif "Cannot write image" in str(er):
        error_text = str(er)
    elif "Cannot read image" in str(er):
        error_text = str(er)
    else:
        error_text = str(er)

    return error_text


class MergerError(Exception):
    pass


class DeletableImage(ft.UserControl):
    def __init__(
        self, file_path: str, delete_image: Callable[["DeletableImage"], None]
    ):
        super().__init__()

        self.file_path = file_path

        self.delete_image = delete_image

        self.preview_image_path = self.file_path
        
        try:
            img = Image.open(self.file_path)
        except PIL.UnidentifiedImageError:
            raise MergerError("Bad image " + self.file_path)
        except OSError:
            raise MergerError("Cannot read image " + self.file_path)

        if img.format not in SUPPORTED_IMAGES_FORMATS:
            raise MergerError("Bad image " + self.file_path)

        # Flet can only display a limited set of image formats.
        # So we make preview files.
        if img.format not in ['JPEG', 'PNG'] :
            preview_maxsize = (512, 512)
            img.thumbnail(preview_maxsize)
            tmp_file = NamedTemporaryFile(delete=False, suffix=".png")
            img.save(tmp_file)
            self.preview_image_path = tmp_file.name
        

    def build(self) -> ft.UserControl:
        return ft.Stack(
            [
                ft.Container(
                    bgcolor="#333333",
                    border_radius=ft.border_radius.all(5),
                    border=ft.border.all(1, ft.colors.BLACK),
                ),
                ft.Container(
                    content=ft.Image(
                        src=self.preview_image_path,
                    ),
                    image_fit=ft.ImageFit.CONTAIN,
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(left=12, right=12, top=40, bottom=12),
                ),
                ft.Container(
                    padding=10,
                    content=ft.Text(Path(self.file_path).name),
                    alignment=ft.alignment.top_left,
                ),
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.icons.CLOSE,
                        icon_color="gray",
                        icon_size=20,
                        on_click=self.remove_clicked,
                    ),
                    alignment=ft.alignment.top_right,
                ),
            ],
            expand=True,
        )

    def get_path(self) -> str:
        return self.file_path

    def remove_clicked(self, e: ft.ControlEvent):
        self.delete_image(self)


class StitchApp(ft.UserControl):
    states = Enum(
        "states",
        [
            "START",
            "IS_STITCHING_IMAGES",
            "IS_NOT_STITCHING_IMAGES",
            "READY",
            "NOT_READY",
            "WORKING",
            "DONE",
            "PROCESS_ERROR",
        ],
    )

    def __init__(self, page: ft.Page):
        self.parent_page = page

        super().__init__()

        self.panorama: Any = None

    def build(self) -> ft.UserControl:
        self.welcom_screen = ft.Ref[ft.Container]()
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
                ft.Text("Images to merge"),
                ft.Stack(
                    expand=True,
                    controls=[
                        ft.Stack(
                            expand=True,
                            ref=self.welcom_screen,
                            visible=True,
                            controls=[
                                ft.Container(
                                    border=ft.border.all(1, "#555555"),
                                    border_radius=ft.border_radius.all(5),
                                ),
                                ft.Container(
                                    padding=40,
                                    alignment=ft.alignment.center,
                                    content=ft.Column(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Image("welcom.png"),
                                            ft.Text(
                                                WELCOME_TEXT,
                                                size=20,
                                                weight=ft.FontWeight.W_300,
                                                text_align=ft.TextAlign.CENTER,
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                        ft.GridView(
                            ref=self.stitching_images,
                            expand=True,
                            runs_count=2,
                            spacing=10,
                            auto_scroll=True,
                            visible=False,
                        ),
                    ],
                ),
                ft.ElevatedButton(
                    ref=self.add_image_button,
                    text="Add images",
                    icon="ADD_PHOTO_ALTERNATE_OUTLINED",
                    bgcolor="#5A7AFF",
                    color="#000000",
                    on_click=self.on_add_image_click,
                ),
                ft.ElevatedButton(
                    ref=self.process_button,
                    text="Merge",
                    icon="BROKEN_IMAGE",
                    height=50,
                    width=150,
                    disabled=True,
                    on_click=self.on_process_button,
                    bgcolor="#5A7AFF",
                    color="#000000",
                ),
            ],
        )

        right_column = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Result image"),
                ft.Stack(
                    expand=True,
                    controls=[
                        ft.Container(
                            content=ft.ProgressRing(
                                ref=self.preloader,
                                width=32,
                                height=32,
                                stroke_width=4,
                                visible=False,
                            ),
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(
                            ref=self.result_image_container,
                            alignment=ft.alignment.center,
                            visible=False,
                            content=ft.Container(
                                image_fit=ft.ImageFit.CONTAIN,
                                content=ft.Image(
                                    ref=self.result_image,
                                    src="",
                                ),
                                bgcolor="#333333",
                                padding=10,
                                border_radius=ft.border_radius.all(5),
                                border=ft.border.all(1, ft.colors.BLACK),
                            ),
                        ),
                    ],
                ),
                ft.ElevatedButton(
                    ref=self.save_result_image_button,
                    visible=False,
                    text="Save image",
                    height=50,
                    width=200,
                    icon="FILE_DOWNLOAD_OUTLINED",
                    on_click=self.on_save_image_click,
                    bgcolor="#5A7AFF",
                    color="#000000",
                ),
            ],
        )

        return [
            ft.Row(
                expand=True,
                controls=[
                    left_column,
                    ft.VerticalDivider(width=30),
                    right_column,
                ],
            )
        ]

    def set_state(self, state: "StitchApp.states") -> None:
        match state:
            case self.states.START:
                self.welcom_screen = True
                self.stitching_images = False
                self.process_button.current.disabled = True
                self.preloader.current.visible = False
                self.result_image_container.current.visible = False
                self.save_result_image_button.current.visible = False

            case self.states.IS_STITCHING_IMAGES:
                self.welcom_screen.current.visible = False
                self.stitching_images.current.visible = True

            case self.states.IS_NOT_STITCHING_IMAGES:
                self.welcom_screen.current.visible = True
                self.stitching_images.current.visible = False

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

            case self.states.PROCESS_ERROR:
                self.preloader.current.visible = False
                self.process_button.current.disabled = False
                self.result_image_container.current.visible = False
                self.save_result_image_button.current.visible = False

        self.update()

    def on_stitching_images_change(self):
        if len(self.stitching_images.current.controls) > 1:
            self.set_state(self.states.READY)
        else:
            self.set_state(self.states.NOT_READY)

        if len(self.stitching_images.current.controls) > 0:
            self.set_state(self.states.IS_STITCHING_IMAGES)
        else:
            self.set_state(self.states.IS_NOT_STITCHING_IMAGES)

    def stitching_image_delete(self, im: DeletableImage) -> None:
        self.stitching_images.current.controls.remove(im)
        self.update()

        self.on_stitching_images_change()

    def on_add_image_click(self, e: ft.ControlEvent):
        folder = None

        if f := self.parent_page.client_storage.get(
            "SmartImageMerger.incoming_user_folder"
        ):
            if Path(f).is_dir():
                folder = f

        if not folder:
            folder = str(Path.home())

        self.file_picker.pick_files(
            initial_directory=folder + os.sep,  # ft.FilePicker needs closing "/"
            allow_multiple=True,
            dialog_title="Select images",
            allowed_extensions=ALLOWED_EXTENSIONS,
        )

    def on_pick_files_dialog(self, e: ft.FilePickerResultEvent):
        if e.files:
            for file in e.files:
                try:
                    im = DeletableImage(file.path, self.stitching_image_delete)
                except MergerError as er:
                    self.show_error(humanize_exceptions(er))
                except Exception as er:
                    self.show_error(humanize_exceptions(er))
                else:
                    self.stitching_images.current.controls.append(im)

            folder = str(PurePath(e.files[0].path).parent)
            self.parent_page.client_storage.set(
                "SmartImageMerger.incoming_user_folder", folder
            )

            self.on_stitching_images_change()

    def show_error(self, text):
        def close_dlg(e):
            error_dlg.open = False
            self.page.update()

        error_dlg = ft.AlertDialog(
            modal=True,
            content=ft.Text(text, size=16),
            content_padding=40,
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("Ok", on_click=close_dlg),
            ],
        )

        self.page.dialog = error_dlg
        error_dlg.open = True
        self.page.update()

    def on_process_button(self, e: ft.ControlEvent):
        self.set_state(self.states.WORKING)

        try:
            imgs = []
            for im_path in self.stitching_images.current.controls:
                img = cv_load_image(im_path.get_path())
                imgs.append(img)

            stitcher = AffineStitcher(crop=False, compensator="gain")
            self.panorama = stitcher.stitch(imgs)

        except MergerError as er:
            self.show_error(humanize_exceptions(er))
            self.set_state(self.states.PROCESS_ERROR)
        except StitchingError as er:
            self.show_error(humanize_exceptions(er))
            self.set_state(self.states.PROCESS_ERROR)
        except OSError as er:
            self.show_error(humanize_exceptions(er))
            self.set_state(self.states.PROCESS_ERROR)
        except Exception as er:
            self.show_error(humanize_exceptions(er))
            self.set_state(self.states.PROCESS_ERROR)
        else:
            result_image_tmp_file = NamedTemporaryFile(delete=False, suffix=".png")
            cv.imwrite(result_image_tmp_file.name, self.panorama)

            self.result_image.current.src = result_image_tmp_file.name
            self.update()

            self.set_state(self.states.DONE)

    def on_save_image_click(self, e: ft.ControlEvent):
        folder = None
        if f := self.parent_page.client_storage.get(
            "SmartImageMerger.incoming_user_folder"
        ):
            if Path(f).is_dir():
                folder = f

        self.file_saver.save_file(
            initial_directory=folder + os.sep,  # ft.FilePicker needs closing "/"
            dialog_title="Save images",
            allowed_extensions=ALLOWED_EXTENSIONS,
            file_name=".png"
        )

    def on_save_dialog(self, e: ft.FilePickerResultEvent):
        if e.path:
            try:
                cv_save_image(self.panorama, e.path)
            except cv.error as er:
                self.show_error(humanize_exceptions(er))
            except MergerError as er:
                self.show_error(humanize_exceptions(er))
            except OSError as er:
                self.show_error(humanize_exceptions(er))
                self.set_state(self.states.PROCESS_ERROR)
            except Exception as er:
                self.show_error(humanize_exceptions(er))


def main(page: ft.Page):
    page.title = "Smart Image Merger"

    page.window_min_width = 900
    page.window_min_height = 650

    page.padding = 30
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.theme.Theme(color_scheme_seed="#1843ff")
    page.update()

    app = StitchApp(page=page)

    # need to display layout correctly, since ft.UserControl is ft.Stack
    app.expand = True

    page.add(app)


if __name__ == "__main__":
    ft.app(target=main)
