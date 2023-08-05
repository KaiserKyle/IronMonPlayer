from log_parse import *

def read_all_files():
    move_table = pd.read_csv('gen3_moveset.csv')
    move_table["move_upper"] = move_table.Name.str.upper()

    results = []

    for i in range(2000):
        results += process_file("d:\\pokerando\\uironmon_seeds\\seed_" + str(i) + ".gba.log", move_table)

    results_df = pd.DataFrame(results, columns=["Player_Pokemon", "Player_Pokemon_Type1", "Player_Pokemon_Type2", "Player_Level", "Rival_Pokemon", "Rival_Level", "Did_Player_Win", "Turns", "One_Hit_KO", "Player_Poke_Legal"])
    print(results_df)
    return results_df

def process_results(results_df):
    print("Player Win Percentage:")
    print(results_df['Did_Player_Win'].value_counts(normalize=True))

    print("Avg Turns: " + str(results_df['Turns'].mean()))

    type1_df = results_df[["Player_Pokemon_Type1", "Did_Player_Win"]].rename(columns={'Player_Pokemon_Type1' : 'Type'})
    type2_df = results_df[["Player_Pokemon_Type2", "Did_Player_Win"]].rename(columns={'Player_Pokemon_Type2' : 'Type'})
    type2_df = type2_df.drop(type2_df[type2_df.Type == ""].index)
    type_wins = pd.concat([type1_df, type2_df], ignore_index=True)

    type_wins.to_csv('type_wins.csv')

    wins_pct_by_type = type_wins.groupby(['Type']).Type.agg(Count = 'count', WinPct = lambda x: type_wins.Did_Player_Win[x.index].sum()/x.count())
    print(wins_pct_by_type.sort_values('WinPct', ascending=False))

    wins_pct_by_legality = results_df.groupby(['Player_Poke_Legal']).Player_Poke_Legal.agg(Count = 'count', WinPct = lambda x: type_wins.Did_Player_Win[x.index].sum()/x.count())
    print(wins_pct_by_legality.sort_values('WinPct', ascending=False))

    one_hit_ko_pct = results_df.groupby(['One_Hit_KO', 'Did_Player_Win'], as_index=False).size()
    print(one_hit_ko_pct)

    poke_counts = results_df.groupby(['Player_Pokemon'])['Player_Pokemon'].agg(Count = 'count', WinPct = lambda x: type_wins.Did_Player_Win[x.index].sum()/x.count()).reset_index().sort_values(['Count'])

    print("Pokemon Popularity:")
    print(poke_counts.head(10))
    print(poke_counts.tail(10))

    print("Pokemon Success Rates:")
    print(poke_counts.sort_values(['WinPct']).head(25))
    print(poke_counts.sort_values(['WinPct']).tail(25))

pd.set_option('display.max_columns', None)

results_df = read_all_files()

process_results(results_df)
