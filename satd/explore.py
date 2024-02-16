import dearpygui.dearpygui as dpg

from satd.search import search

def search_callback():
    collection = search()
    print(collection)

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(label="Example Window"):
    dpg.add_text("Hello world")
    dpg.add_input_text(label="string")
    dpg.add_slider_float(label="float")
    dpg.add_button(label="Search", callback=search_callback)

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()