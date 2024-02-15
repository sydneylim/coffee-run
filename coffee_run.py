import numpy as np
import pandas as pd
import sys
import argparse
from datetime import datetime

def main():
    # read in previous coffee run data, convert into dataframe
    filepath = "coffee_run_data.csv"

    # if file doesn't exist, create empty df
    try:
        coffee_data = pd.read_csv(filepath, index_col=0)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        coffee_data = pd.DataFrame(columns=['Payer', 'Total'])

    # read command line arguments
    args = sys.argv
    
    # HELP MENU
    # "python coffee_run.py"
    if len(args) == 1:
        help(filepath)

    # ADD NEW COFFEE RUN
    elif args[1] == "add_run":
        # "python coffee_run.py add_run [payer] [consumer price] ..."
        if len(args) > 2:
            coffee_data = add_run(coffee_data, args[2:])
        
        # "python coffee_run.py add_run"
        else:
            payer = input("Input [payer name]: ")
            new_run_data = [payer]
            print("\nInput the name of every person that went on the coffee run and the price of their drink.\nType 'Done' when finished.\n")
            drink = input("Input [consumer name] [cost]: ")

            while(drink != "Done"):
                new_run_data = new_run_data + drink.split(" ")
                drink = input("Input [name] [cost]: ")
            
            coffee_data = add_run(coffee_data, new_run_data)
        
        print(coffee_data)
        coffee_data.to_csv(filepath)

    # CALCULATE NEXT COFFEE RUN PAYER
    elif args[1] == "calc_payer":
        # "python coffee_run.py calc_payer [absent name] ..."
        if len(args) > 2:
            next_payer = calc_payer(coffee_data, args[2:])
        
        # "python coffee_run.py calc_payer"
        else:
            next_payer = calc_payer(coffee_data, [])
        
        print(next_payer)

    # DELETE EXISTING COFFEE RUN
    elif args[1] == "delete_run":
        # "python coffee_run.py delete_run [run date] [run time]"
        if len(args) > 2:
            coffee_data = delete_run(coffee_data, " ".join(args[2:]))
        
        # "python coffee_run.py delete_run"
        else:
            delete_run_date = input("Input datetime of run to delete: ")
            coffee_data = delete_run(coffee_data, delete_run_date)
        
        print(coffee_data)
        coffee_data.to_csv(filepath)

    # EDIT EXISTING COFFEE RUN
    elif args[1] == "edit_run":
        # "python coffee_run.py edit_run [run date] [run time] Payer [new payer name]"
        # "python coffee_run.py edit_run [run date] [run time] Drink [consumer name] [price]"
        if len(args) > 2:
            edit_run_date = " ".join(args[2:4])
            edit_type = args[4]

            if edit_type == "Payer":
                new_payer = args[5]
                coffee_data = edit_run_payer(coffee_data, edit_run_date, new_payer)

            elif edit_type == "Drink":
                new_drink = " ".join(args[5:7])
                coffee_data = edit_run_drink(coffee_data, edit_run_date, new_drink)
        
        # "python coffee_run.py edit_run"
        else:
            edit_run_date = input("Input the datetime of the coffee run to edit: ")
            edit_type = input("Would you like to edit the payer name or add/edit a drink? [Payer/Drink]: ")
            
            if edit_type == "Payer":
                new_payer = input("Payer name: ")
                coffee_data = edit_run_payer(coffee_data, edit_run_date, new_payer)

            elif edit_type == "Drink":
                new_drink = input("Input [name] [cost]: ")
                coffee_data = edit_run_drink(coffee_data, edit_run_date, new_drink)

            else:
                print("Invalid option.")
                return
            
        print(coffee_data)
        coffee_data.to_csv(filepath)

    # GET COFFEE RUN HISTORY
    # "python coffee_run.py history"    
    elif args[1] == "history":
        history(coffee_data)

    # UNKNOWN COMMAND -- help menu
    else:
        help(filepath)


# function to calculate whose turn it is to pay
# calculated by who is "most in debt", meaning who has paid the least relative to the amount they spent
# chosen among the people present for that run
def calc_payer(coffee_data, absent):
    consumers = [c for c in coffee_data.columns if c not in absent and coffee_data.columns.get_loc(c) != 0 and coffee_data.columns.get_loc(c) != 1]
    payment_history = {}
    
    for c in consumers:
        total_spent = coffee_data[c].sum()
        if c not in coffee_data['Payer'].values:
            total_paid = 0.0
        else:
            total_paid = (coffee_data.groupby(['Payer']).sum().reset_index())
            total_paid = total_paid.loc[total_paid['Payer'] == c, 'Total'].iloc[0]
        
        owed = total_spent - total_paid
        payment_history[c] = owed
    
    return max(payment_history, key=payment_history.get)


# function to record who got what drink, how much each drink was, and who paid for that day
# indexed by datetime when the coffee run data is added
def add_run(coffee_data, args):
    payer = args[0]
    names = args[1::2]
    prices = [float(a) for a in args[2::2]]

    new_run = pd.DataFrame({'columns':['Payer', 'Total']+names, 
                            'values': [payer, sum(prices)]+prices,
                            'date': datetime.now().strftime("%m/%d/%Y %H:%M:%S")})
    
    new_run = new_run.pivot(columns='columns', values='values', index='date')
    coffee_data = pd.concat([coffee_data, new_run])
    
    return coffee_data 

# function to remove a recorded coffee run, given the datetime of the coffee run
def delete_run(coffee_data, args):
    # print(coffee_data.loc[coffee_data.index == args])
    coffee_data = coffee_data.drop(args)
    return coffee_data

# function to edit the payer of a recorded coffee run
def edit_run_payer(coffee_data, edit_run_date, new_payer):
    coffee_data.loc[[edit_run_date], ['Payer']] = new_payer
    return coffee_data

# function to (1) add a consumer and their drink, or (2) edit an existing drink price, to a recorded coffee run
def edit_run_drink(coffee_data, edit_run_date, new_drink):
    consumer = new_drink.split(" ")[0]
    new_price = float(new_drink.split(" ")[1])

    if consumer not in coffee_data:
        coffee_data[consumer] = np.nan
    
    coffee_data.loc[[edit_run_date], [consumer]] = new_price
    consumers = [c for c in coffee_data.columns if c != 'Payer' and c != 'Total']
    coffee_data.loc[[edit_run_date], ['Total']] = coffee_data.loc[[edit_run_date], consumers].sum(axis=1)

    return coffee_data

# function to display all recorded coffee runs
def history(coffee_data):
    if coffee_data.empty:
        print("No coffee runs recorded.")
    else:
        print(coffee_data.fillna("-"))

# function to display program functionality
def help(filepath):
    print("------------------------- COFFEE RUNS -------------------------")
    print("---------------- Whose turn is it to pay today?----------------")
    print("---------------------------------------------------------------\n")
    print("When a group of coworkers go on a coffee run, only one coworker \n\
pays for all the coffees to ease the checkout process. \n\
Considering that not all drinks cost the same, they encounter \n\
a problem every day: Whose turn is it to pay today?\n")
    print("---------------------------------------------------------------\n")
    print("Data persistently stored at: ", filepath)

    
    print("Usage: python coffee_run.py <command> [arguments]")
    print()
    print("Commands:")
    print('  calc_payer [absent name] -- Calculate whose turn it is to pay. Add in anyone not present for the next coffee run to be excluded from being selected as the next payer.')
    print('  add_run [payer name] [consumer name] [consumer price] ... -- Record who paid today, and how much everyones drinks cost')
    print('  edit_run [run date] [run time] [Payer/Drink] [New Payer Name/New Consumer Name and Price] -- edit data on a past coffee run')
    print('  delete_run [run date] [run time] -- delete data on a past coffee run')
    print('  history -- get all past coffee run data')
    print('  help -- display help menu')


if __name__=="__main__":
    main()