#!/usr/bin/python3
import os
import sys
import threading

import PySimpleGUI as sg

import LogParser
from asset_utils import get_card_path
from player import Player

player_ids = []


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    return os.path.join(os.path.abspath(".."), relative_path)


def construct_player_layout(player: Player, index: int):
    ind = str(index)
    layout = [
        [sg.Text("Health: 40", font="Courier 20", key=f"{index}health")],
        [sg.Image(get_card_path(player.get_minion(1).name, "", False), pad=((300, 0), 0), key=ind + "0"),
         sg.Image(get_card_path(player.get_minion(2).name, "", False), key=ind + "1"),
         sg.Image(get_card_path(player.get_minion(3).name, "", False), key=ind + "2"),
         sg.Image(get_card_path(player.get_minion(4).name, "", False), key=ind + "3")],
        [sg.Image(get_card_path(player.get_minion(5).name, "", False), pad=((400, 0), 0), key=ind + "4"),
         sg.Image(get_card_path(player.get_minion(6).name, "", False), key=ind + "5"),
         sg.Image(get_card_path(player.get_minion(7).name, "", False), key=ind + "6")],
        [sg.Image(get_card_path(player.get_treasure(1), "", False), key=ind + "7"),
         sg.Image(get_card_path(player.get_treasure(2), "", False), key=ind + "8"),
         sg.Image(get_card_path(player.get_treasure(3), "", False), pad=((0, 500), 0), key=ind + "9"),
         sg.Image(get_card_path(player.get_treasure(3), "", False), key=ind + "10"),
         sg.Image(get_card_path(player.hero if player.hero else "empty", "", False), key=ind + "11")]
    ]
    return layout


def get_tab_key(index: int):
    return f"-{index}-"


def update_player(window: sg.Window, update: LogParser.Update):
    state = update.state
    index = get_player_index(state.playerid)
    player_tab = window[get_tab_key(index)]
    title = f"{state.heroname}" if state.health > 0 else f"{state.heroname} *DEAD*"
    player_tab.update(title=title)
    window[f"{index}{11}"].update(filename=get_card_path(state.heroname, state.heroid, False))
    window[f"{index}health"].update(f"Health: {state.health}")


def update_board(window: sg.Window, update: LogParser.Update):
    for playerid, actions in update.state.items():
        for action in actions:
            slot = action.slot
            zone = action.zone
            position = 10 if zone == 'Spell' else (7 + int(slot)) if zone == "Treasure" else slot
            update_card(window, playerid, position, action.cardname, action.content_id, action.is_golden)


def update_card(window: sg.Window, playerid: str, position, cardname: str, content_id: str, is_golden: bool):
    index = get_player_index(playerid)
    if index > 0:
        window[f"{index}{position}"].update(filename=get_card_path(cardname, content_id, is_golden))


def get_player_index(player_id: str):
    if player_id not in player_ids:
        player_ids.append(player_id)
    return player_ids.index(player_id) + 1


def the_gui():
    """
    Starts and executes the GUI
    Reads data from a Queue and displays the data to the window
    Returns when the user exits / closes the window
    """
    sg.theme('Dark Blue 14')

    tabs_layout = []
    for num in range(1, 9):
        name = "Player" + str(num)
        tabs_layout.append(sg.Tab(layout=construct_player_layout(Player(name=name, id="test", last_seen=0, hero="",
                                                                        treasures={}, minions={}, spell="", health=40,
                                                                        level=1), num), title=name,
                                  k=get_tab_key(num)))

    tabgroup = [[sg.TabGroup(layout=[tabs_layout])]]

    layout = [[sg.Text(text="Waiting for match to start...", font="Courier 32", k="-GameStatus-",
                       justification='center')], tabgroup]

    window = sg.Window('SBBTracker', layout, resizable=True, finalize=True, size=(1920, 1080),
                       icon=resource_path("sbbt.ico"))
    threading.Thread(target=LogParser.run, args=(window,), daemon=True).start()

    # --------------------- EVENT LOOP ---------------------
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == LogParser.JOB_NEWGAME:
            print("Game started!")
            for id in player_ids:
                for pos in range(11):
                    update_card(window, id, pos, "empty", "", False)
            player_ids.clear()
            window["-GameStatus-"].update("Round: 0")
        elif event == LogParser.JOB_ROUNDINFO:
            print("Round info event")
            window["-GameStatus-"].update(f"Round: {values[event][1].round}")
        elif event == LogParser.JOB_PLAYERINFO:
            print("Player info event")
            updated_player = values[event]
            update_player(window, updated_player)
        elif event == LogParser.JOB_BOARDINFO:
            print("Board info event")
            update_board(window, values[event])

    # if user exits the window, then close the window and exit the GUI func
    window.close()
    try:
        os.remove(LogParser.offsetfile)
    except:
        print("Couldn't delete offset!")


if __name__ == '__main__':
    the_gui()
    print('Exiting Program')
