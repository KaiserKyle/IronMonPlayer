import pandas as pd
from io import StringIO
from helper import *

def get_starters(dex, st1, st2, st3):
    return dex.loc[(dex.NAME == st1) | (dex.NAME == st2) | (dex.NAME == st3)]

def get_starters_moves(starters, move_dex):
    starter_moves_index = move_dex.NUM.isin(starters.NUM)
    return move_dex[starter_moves_index]

def parse_pokedex(lines, index):
    datatable_str = lines[index + 1]
    for i in range(index + 2, index + 388):
        datatable_str += lines[i]

    table_io = StringIO(datatable_str)
    
    df =  pd.read_table(table_io, sep="|")
    df.columns = df.columns.str.strip()

    df = df.applymap(lambda x: x.strip() if type(x) == str else x)

    return df

def read_moves_for_pokemon(lines, i):
    rows = []
    pokedex_num = int(lines[i].split()[0])
    pokemon_name = lines[i].split()[1]
    i = i + 7
    while lines[i].strip() != "":
        level = int(lines[i].split()[1].strip(":"))
        move = lines[i].split(":")[1].strip()
        rows.append([pokedex_num, pokemon_name, level, move])
        i += 1

    return rows, i

def read_moves(lines, index):
    rows = []
    i = index + 1
    while lines[i].strip() != "":
        new_rows, new_index = read_moves_for_pokemon(lines, i)
        rows += new_rows
        i = new_index + 1
    
    df = pd.DataFrame(rows, columns=["NUM", "NAME", "LEVEL", "MOVE"])

    return df

def process_file(filename, move_table):
    print(filename)
    with open(filename) as file:
        lines = file.readlines()
        starter_1, starter_2, starter_3 = "", "",""
        pokedex, move_dex = "", ""
        for i in range(0, len(lines)):
            if lines[i].startswith('--Random Starters--'):
                starter_1 = lines[i+1].split(" ", 4)[-1].strip()
                starter_2 = lines[i+2].split(" ", 4)[-1].strip()
                starter_3 = lines[i+3].split(" ", 4)[-1].strip()
            elif lines[i].startswith("--Pokemon Base Stats & Types--"):
                pokedex = parse_pokedex(lines, i)
            elif lines[i].startswith("--Pokemon Movesets--"):
                move_dex = read_moves(lines, i)
                

    starters_df = get_starters(pokedex, starter_1, starter_2, starter_3)
    print("Starters:")
    print(starters_df)
    print()
    if (len(starters_df) != 3):
        print("ERROR: Starters != 3")

    starter_moves = get_starters_moves(starters_df, move_dex)
    starter_moves = starter_moves.merge(move_table, how='left', left_on='MOVE', right_on = 'move_upper')

    missing = starter_moves[starter_moves.isna().any(axis=1)]
    if (missing.empty == False):
        print("Missing Moves:")
        print(starter_moves[starter_moves.isna().any(axis=1)])

    #print("Starter Moves:")
    #print(starter_moves)

    # Rival picks one to the left.
    # Frist column is player pokemon, second column is rival's
    matchups = [[starter_1, starter_2],
                [starter_2, starter_3],
                [starter_3, starter_1]]
            
    results = []

    for matchup in matchups:
        player_poke = create_pokemon(starters_df.loc[starters_df.NAME == matchup[0]].iloc[0], 5, starter_moves)
        rival_poke = create_pokemon(starters_df.loc[starters_df.NAME == matchup[1]].iloc[0], 8, starter_moves)
        print(player_poke)
        print("VS")
        print(rival_poke)
        # Player will choose their move based on EV, as they do not know opponent's stats
        # Rival will cheat and choose a move based on damage
        move_choices = calculate_move_potency(player_poke, rival_poke).sort_values(by=['EV'], ascending=False)
        rival_move_choices = calculate_move_potency(rival_poke, player_poke).sort_values(by=['Damage'], ascending=False)
        print("Player Moves Ranked:")
        print(move_choices)
        print("Rival Moves Ranked:")
        print(rival_move_choices)
        print()

        # Figure out the winner
        player_wins = False
        speed_matters = move_choices.iloc[0].Turns_To_Kill == rival_move_choices.iloc[0].Turns_To_Kill
        if (not speed_matters):
            player_wins = move_choices.iloc[0].Turns_To_Kill < rival_move_choices.iloc[0].Turns_To_Kill
        else:
            player_wins = calcStat(player_poke.speed, 15, 0, player_poke.level, 0) > calcStat(rival_poke.speed, 15, 0, rival_poke.level, 0)

        # Victory Metadata
        turns_to_win = min(move_choices.iloc[0].Turns_To_Kill, rival_move_choices.iloc[0].Turns_To_Kill)
        one_hit_ko = False
        # NOTE Need to take priority moves into consideration
        if turns_to_win == 1:
            one_hit_ko = True

        results.append([player_poke.name, player_poke.type1, player_poke.type2, player_poke.level, rival_poke.name, rival_poke.level, player_wins, turns_to_win, one_hit_ko, is_pokemon_legal(player_poke)])

    return results