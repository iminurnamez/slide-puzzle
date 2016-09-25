from . import prepare,tools
from .states import title_screen, puzzling

def main():
    controller = tools.Control(prepare.ORIGINAL_CAPTION)
    states = {"TITLE": title_screen.TitleScreen(),
                   "PUZZLING": puzzling.Puzzling()}
    controller.setup_states(states, "TITLE")
    controller.main()
