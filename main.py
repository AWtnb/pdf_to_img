from pathlib import Path

import fitz
import flet as ft


# https://flet.dev/docs/guides/python/getting-started/

def main(page: ft.Page):
    page.title = "pdf to image converter"
    page.theme_mode = "light"

    target_file = ft.Ref[ft.Text]()
    output_folder = ft.Ref[ft.Text]()
    result_message = ft.Ref[ft.Text]()
    dpi_slider = ft.Ref[ft.Slider]()
    ui_rows = []


    ###################################
    # file picker
    ###################################

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            target_file.current.value = e.files[0].path
            output_folder.current.value = str(Path(target_file.current.value).parent)
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    def show_file_picker(_: ft.FilePickerResultEvent):
        file_picker.pick_files(
            allow_multiple=False,
            file_type="custom",
            allowed_extensions=["pdf"]
        )

    file_pick_row = ft.Row(controls=[
        ft.ElevatedButton("Select PDF", on_click=show_file_picker),
        ft.Text(ref=target_file)
    ])
    ui_rows.append(file_pick_row)


    ###################################
    # folder picker
    ###################################

    def on_folder_picked(e: ft.FilePickerResultEvent):
        if e.path:
            output_folder.current.value = e.path
            page.update()

    folder_picker = ft.FilePicker(on_result=on_folder_picked)
    page.overlay.append(folder_picker)

    def show_pick_folder(_: ft.FilePickerResultEvent):
        folder_picker.get_directory_path()

    folder_pick_row = ft.Row(controls=[
        ft.ElevatedButton("Select Output Folder", on_click=show_pick_folder),
        ft.Text(ref=output_folder)
    ])
    ui_rows.append(folder_pick_row)


    ###################################
    # execute button
    ###################################

    def convert_to_image(file_path:str, out_dir_path:str, dpi:int=300):
        pdf_path = Path(file_path)
        pdf = fitz.open(str(pdf_path))
        for i, p in enumerate(pdf):
            out_path = Path(out_dir_path, pdf_path.stem + "_{:03}.png".format(i+1))
            pix = p.get_pixmap(dpi=dpi)
            pix.save(out_path)
            result_message.current.value = "converted page {:03}/{:03}".format(i+1, len(pdf))
            page.update()

    def execute_convert(_: ft.FilePickerResultEvent):
        if not target_file.current.value or not output_folder.current.value:
            return
        result_message.current.value = ""
        if Path(target_file.current.value).suffix == ".pdf":
            ui_controls.disabled = True
            convert_to_image(target_file.current.value, output_folder.current.value, int(dpi_slider.current.value))
            ui_controls.disabled = False
            result_message.current.value = "FINISHED!"
        else:
            result_message.current.value = "Not a PDF file..."
        page.update()


    execute_row = ft.Row(controls=[
        ft.ElevatedButton("Convert!", on_click=execute_convert),
        ft.Slider(ref=dpi_slider, min=100, max=900, divisions=10, label="dpi: {value}", value=500)
    ])
    ui_rows.append(execute_row)


    ###################################
    # render page
    ###################################

    ui_rows.append(ft.Text(ref=result_message))
    ui_controls = ft.Column(controls=ui_rows)
    page.add(ui_controls)


ft.app(target=main)