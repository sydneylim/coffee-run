import numpy as np
import pandas as pd
import sys
from datetime import datetime

def main():
    # read in previous coffee run data, convert into dataframe
    filepath = "coffee_run_data.csv"

    # if file doesn't exist, create empty df
    try:
        coffee_data = pd.read_csv(filepath, index_col=0)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        coffee_data = pd.DataFrame(columns=['Payer', 'Total'])

    # initialize table with Payer and Total columns to pin them to the left if all entries deleted
    if coffee_data.empty:
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
            payer = input("Input <payer name>: ")

            if len(payer) == 0:
                print("Invalid payer name.")
                return
            
            new_run_data = [payer]

            print("\nInput the name of every person that went on the coffee run and \n\
the price of their drink, one pair at a time, separated by a space. \n\
Names must be unique and have no spaces. Do not leave any of the prompts empty. \n\
EXAMPLE: Alice 2.5 \n\n\
Type 'Done' when finished.\n")
            
            drink = input("Input <consumer name> <drink cost> (Type 'Done' when finished): ")

            while(drink != "Done"):
                new_run_data = new_run_data + drink.split(" ")
                drink = input("Input <consumer name> <drink cost> (Type 'Done' when finished): ")
            
            coffee_data = add_run(coffee_data, new_run_data)
        
        # print()
        # history(coffee_data)
        # print("\nSuccessfully added coffee run.")

        try:
            coffee_data.to_csv(filepath)
        except AttributeError:
            return

    # CALCULATE NEXT COFFEE RUN PAYER
    elif args[1] == "calc_payer":
        # "python coffee_run.py calc_payer [absent name] ..."
        if len(args) > 2:
            calc_payer(coffee_data, args[2:])
        
        # "python coffee_run.py calc_payer"
        else:
            calc_payer(coffee_data, [])
        
    # DELETE EXISTING COFFEE RUN
    elif args[1] == "delete_run":
        # "python coffee_run.py delete_run [run date] [run time]"
        if len(args) > 2:
            coffee_data = delete_run(coffee_data, " ".join(args[2:]))
        
        # "python coffee_run.py delete_run"
        else:
            delete_run_date = input("Input datetime of run to delete: ")
            coffee_data = delete_run(coffee_data, delete_run_date)
        
        coffee_data = coffee_data.loc[:, (coffee_data!=0).any(axis=0)]
        coffee_data.dropna(how='all', axis=1, inplace=True)
        coffee_data.to_csv(filepath)

    # EDIT EXISTING COFFEE RUN
    elif args[1] == "edit_run":
        # "python coffee_run.py edit_run [run date] [run time] Payer [new payer name]"
        # "python coffee_run.py edit_run [run date] [run time] Drink [consumer name] [price]"
        if len(args) > 2:
            edit_run_date = " ".join(args[2:4])

            try:
                coffee_data.loc[edit_run_date]
            except KeyError:
                print("Run with given datetime not found.")
                return

            try:
                edit_type = args[4]
            except IndexError:
                print("Invalid edit type.")
                return

            if edit_type == "Payer":
                try:
                    new_payer = args[5]
                except IndexError:
                    print("Invalid new payer name.")
                    return
                
                coffee_data = edit_run_payer(coffee_data, edit_run_date, new_payer)

            elif edit_type == "Drink":
                if len(args[5:7]) != 2:
                    print("Invalid drink data.")
                    return
                
                new_drink = " ".join(args[5:7])             
                coffee_data = edit_run_drink(coffee_data, edit_run_date, new_drink)
            else:
                print("Invalid option.")
                return
        
        # "python coffee_run.py edit_run"
        else:
            edit_run_date = input("Input the datetime of the coffee run to edit: ")

            try:
                coffee_data.loc[edit_run_date]
            except KeyError:
                print("Run with given datetime not found.")
                return

            edit_type = input("Would you like to edit the payer name or add/edit a drink? [Payer/Drink]: ")
            
            if edit_type == "Payer":
                new_payer = input("Input <new payer name>: ")
                if len(new_payer) == 0:
                    print("Invalid new payer name.")
                    return
                
                coffee_data = edit_run_payer(coffee_data, edit_run_date, new_payer)

            elif edit_type == "Drink":
                new_drink = input("Input <consumer name> <drink cost>: ")
                if len(new_drink.split(" ")) != 2:
                    print("Invalid drink data.")
                    return
                
                coffee_data = edit_run_drink(coffee_data, edit_run_date, new_drink)

            else:
                print("Invalid option.")
                return

        coffee_data = coffee_data.loc[:, (coffee_data!=0).any(axis=0)]
        coffee_data.dropna(how='all', axis=1, inplace=True)
        print()
        history(coffee_data)
        print()
        print("Successfully edited coffee run data from", edit_run_date)
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
    consumers = [c for c in coffee_data.columns if c not in absent and c != "Payer" and c != "Total"]
    payment_history = {}
    
    if len(consumers) == 0 or coffee_data.empty:
        print("No previous consumers found.")
        return
    
    for c in consumers:
        total_spent = coffee_data[c].sum()
        if c not in coffee_data['Payer'].values:
            total_paid = 0.0
        else:
            total_paid = (coffee_data.groupby(['Payer']).sum().reset_index())
            total_paid = total_paid.loc[total_paid['Payer'] == c, 'Total'].iloc[0]
        
        owed = total_spent - total_paid
        payment_history[c] = owed
    
    print("The next payer is:", max(payment_history, key=payment_history.get))


# function to record who got what drink, how much each drink was, and who paid for that day
# indexed by datetime when the coffee run data is added
def add_run(coffee_data, args):
    payer = args[0]
    names = args[1::2]

    try:
        prices = [float(a) for a in args[2::2]]
    except ValueError:
        print("Invalid drink data.")
        return

    if len(names) == 0 or len(prices) == 0:
        print("Invalid drink data.")
        return
    
    try:
        new_run = pd.DataFrame({'columns':['Payer', 'Total']+names, 
                                'values': [payer, sum(prices)]+prices,
                                'date': datetime.now().strftime("%m/%d/%Y %H:%M:%S")})

        new_run = new_run.pivot(columns='columns', values='values', index='date')

    except ValueError:
        print("Invalid drink data.")
        return
    
    coffee_data = pd.concat([coffee_data, new_run])
    
    print()
    history(coffee_data)
    print("\nSuccessfully added coffee run.")
    
    return coffee_data 

# function to remove a recorded coffee run, given the datetime of the coffee run
def delete_run(coffee_data, args):    
    try:
        coffee_data = coffee_data.drop(args)
        history(coffee_data)
        print()
        print("Successfully deleted coffee run data from", args)

    except KeyError:
        print("Run with given datetime not found.")
    
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
    print("==================================== COFFEE RUN ====================================")
    print("-------------------------- Whose turn is it to pay today? --------------------------")
    print("------------------------------------------------------------------------------------")
    print("When a group of coworkers go on a coffee run, only one coworker pays for all the \n\
coffees to ease the checkout process. Considering that not all drinks cost the \n\
same, they encounter a problem every day: Whose turn is it to pay today?")
    print("====================================================================================\n")
    print("====================================== NOTES =======================================")
    print("Data persistently stored at: ", filepath)
    print("------------------------------------------------------------------------------------")
    print("REQUIREMENTS:\n\
    - all names and prices cannot contain spaces\n\
    - all prices must be valid numbers\n\
    - no names are 'Payer' or 'Total'\n\
    - all names must be unique\n\
    - all datetime arguments are formatted as follows: mm/dd/YYYY HH:MM:SS\n\
    - all commands and arguments are case sensitive\n\
    - the persistent data file cannot be open while the program is being used\n\
    - only one coffee run can be added per second")
    print("====================================================================================\n")

    print("====================================== USAGE =======================================")

    print("usage: python coffee_run.py <command> [arguments]")
    print("------------------------------------------------------------------------------------")
    print("The following commands will be used interactively if no arguments are specified:")
    print("    add_run\n    edit_run\n    delete_run")
    print("------------------------------------------------------------------------------------")

    print("commands:")
    print("    calc_payer   -- calculate whose turn it is to pay next \n\
                    optional: specify anyone not present to pay\n")
    print("    add_run      -- record new coffee run data\n")
    print("    edit_run     -- edit data on a past coffee run, including \n\
                    modifying the payer, modifying an existing drink, \n\
                    or adding another consumer\n")
    print("    delete_run   -- delete data on a past coffee run\n")
    print("    history      -- view all past coffee run data\n")
    print("    help         -- display this help menu")

    print("------------------------------------------------------------------------------------")
    print("syntax for options:")
    print('    calc_payer [absent_name] ...\n\
        [absent_name] -- specify a list of people not present, so they will not be \n\
                         selected to pay. if no names are specified, all consumers \n\
                         of past coffee runs will be included in calculating whose \n\
                         turn it is to pay. each name must be a single word, \n\
                         separated by a space.')
    print("------------------------------------------------------------------------------------")
    print("syntax for command line (non-interactive) use:")
    print('    add_run <payer_name> <consumer_name> <consumer_price> ...\n\
        <payer_name>                     -- the first argument must specify the \n\
                                            name of the payer\n\n\
        <consumer_name> <consumer_drink> -- the name of a consumer that went on \n\
                                            a coffee run, followed by the price \n\
                                            of their drink. if there are multiple \n\
                                            consumers, simply list the names and \n\
                                            prices in pairs separated by a space.\n')

    print('    edit_run <datetime> <type> <payer_data, drink_data>\n\
        <datetime>   -- the first argument must specify the datetime of the run \n\
                        to be edited, formatted as mm/dd/YYYY HH:MM:SS.\n\n\
        <type>       -- the second argument must specify the editing type. \n\
                        options: [Payer, Drink]\n\
                        - Payer: modifies the payer name of the specified run. \n\
                                 must be followed by <payer_data>.\n\
                        - Drink: modifies the drink data of the specified run. \n\
                                 must be followed by <drink_data>. \n\n\
        <payer_data> -- specifies the new payer name. \n\n\
                        used when the type selected is <Payer>.\n\n\
        <drink_data> -- specifies a consumer name, followed by the price of \n\
                        their drink, separated by a space. if the consumer \n\
                        was already in the specified coffee run, the previous \n\
                        price will be overwritten. if the consumer was not in the \n\
                        specified coffee run, they will be added to that\n\
                        coffee run. if the consumer has not previously been a \n\
                        part of any coffee runs, they will be added to the \n\
                        coffee run history table. \n\n\
                        used when the type selected is <Drink>. \n')
    
    print('    delete_run <datetime>\n\
        <datetime> -- the first argument must specify the datetime of the run \n\
                      to be edited, formatted as mm/dd/YYYY HH:MM:SS.\n')
    print("====================================================================================\n")


if __name__=="__main__":
    main()