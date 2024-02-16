# coffee-run ☕
When a group of coworkers go on a coffee run, only one coworker pays for all the coffees each day to ease the checkout process. Considering that all not drinks cost the same, they encounter a problem every day: Whose turn is it to pay for coffee?

## Solution
To calculate whose turn it is to pay, we keep track of:
1. Who pays for each coffee run
2. The cost of each consumer's drink on every coffee run

From this information, we can calculate:
1. The total amount that each person has paid across all coffee runs
2. The total cost of the coffee consumed by each person across all coffee runs

Then, we find the difference between (1) and (2) from above to find the amount that each person "owes". The person that has consumed the most coffee by cost, minus the amount that they have paid for everyone's coffee, is calculated to be the next payer.

## Implementation
### Functionality
This program can record, edit, and delete data of each coffee run, including who paid for all of the drinks and the cost of each coffee consumer's drink. Using that data, it can calculate whose turn it is to pay. The coffee run data is stored in a table uniquely indexed by the datetime of when each coffee run is added. We can view the entire table to see data on all past coffee runs.

### Design
This program uses a command line interface. Some commands will have an option to either be used interactively (the user will be prompted to enter data), or through command line arguments. The syntax for both will be specified under **Usage**.

### Data Storage
The coffee run data will be persistently stored in a `.csv` file. The filename can be found through the help menu under **Notes**:
```
python coffee_run.py help
```
> [!NOTE]
> The filename and location and can be changed in the `main` function by modifying the `filepath` variable. `filepath` must specify a filename with a `.csv` extension, and will be created in `/coffee-run` if no path is specified. If the file exists, it will read the `.csv`. If the file does not exist, it will be created.

We provide sample data at `/coffee-run/coffee_run_data.csv`.

>[!WARNING]
> The `.csv` file where the data is stored cannot be open while the program is being used.

### Requirements
This program is written in Python 3. To run it, you will need to have Python 3 installed, as well as the following packages:
- numpy
- pandas

## Usage
To run the program, use the following general syntax:
```
python coffee_run.py <command> [args]
```
### Commands Overview
| Command | Description |
| --- | --- |
| `calc_payer` | Calculate whose turn it is to pay next. Optionally, specify anyone not present to pay. |
| `add_run` | Record new coffee run data. |
| `edit_run` | Edit data on a past coffee run, including modifying the payer, modifying the price of an existing consumer's drink, or adding another consumer's drink's price to the run. |
| `delete_run` | Delete data on a past coffee run. |
| `history` | View all past coffee run data. |
| `help` | Display help menu detailing how to use this program. |

> [!IMPORTANT]
> The following commands are _non-interactive_. `calc_payer` takes an optional argument, described under **Options**. `history` and `help` do not accept arguments.
> - `calc_payer`
> - `history`
> - `help`

> [!IMPORTANT]
> The following commands will be used _interactively_ (the user will be prompted to enter data) if no arguments are specified. They may be used _non-interactively_ by providing the necessary data via command line arguments. The syntax for doing so is outlined in **Command Line (Non-Interactive) Use**.
> - `add_run`
> - `edit_run`
> - `delete_run`<br>

> [!CAUTION]
> The following are restrictions to this program:
> - The `.csv` file where the data is stored cannot be open while the program is being used.
> - All commands and arguments are case-sensitive
> - All names and prices specified cannot contain spaces
> - No names can be "Payer" or "Total"
> - All prices must be valid numbers
> - All datetime arguments must be formatted as `mm/dd/YYYY HH:MM:SS`
> - Only one coffee run can be added per second

### Options
#### calc_payer
The `calc_payer` command can optionally specify a list of people not present, so they will not be selected to pay. If no names are specified, all consumers of past coffee runs will be included in calculating whose turn it is to pay. Each name must be a single word, separated by a single space. The syntax is as follows:
```
calc_payer [absent 1_name] [absent 2_name] ...
```
### Command Line (Non-Interactive) Use:
`add_run`, `edit_run`, and `delete_run` can be used non-interactively by specifying the necessary data via command line arguments. We outline the syntax below.

#### add_run
```
add_run <payer_name> <consumer 1_name> <consumer 1_price> <consumer 2_name> <consumer 2_price> ...
```
| Argument | Description |
| --- | --- |
| `<payer_name>` | The first argument must specify the name of the payer. |
| `<consumer_name>` | The name of a consumer that went on the coffee run. Must be followed by the price of the consumer's drink. |
| `<consumer_price>` | The price of a consumer's drink. Must be preceded by the consumer's name. |

The first argument must specify the payer name. The following arguments must be paired into each consumer's name, and the price of their drink, separated by a space. If there are multiple consumers, simply list the names and prices in pairs separated by a space.

For example, the following coffee run data entered on 02/14/2024 at 12\:00\:00:
```
python coffee_run.py add_run Alice Alice 2.5 Bob 3 Carol 4.5
```
will result in this coffee run entry:
|  | Payer | Total | Alice | Bob | Carol |
| --- | --- | --- | --- | --- | --- |
| 02/14/2024 12\:00:00 | Alice | 10.0 | 2.5 | 3.0 | 4.5 |

#### edit_run
```
edit_run <datetime> <type> <payer_data, drink_data>
```
| Argument | Description |
| --- | --- |
| `<datetime>` | The first argument must specify the datetime of the run to be edited, formatted as `mm/dd/YYYY HH:MM:SS`. |
| `<type>` | The second argument must specify the type of data to be edited. <br> **Options**: [Payer, Drink] <br> `Payer`: Modifies the payer name of the specified run. Must be followed by `<payer data>`. <br> `Drink`: Modifies the drink data of a specified run. Must be followed by `<drink data>`. |
| `<payer_data>` | Specifies the new payer name for the specified run. <br><br> Used when the type selected is `Payer`. |
| `<drink_data>` | Specifies the consumer name, followed by the price of their drink, separated by a space. If the consumer was already in the specified coffee run, the previously recorded price will be overwritten. If the consumer was not in the specified coffee run, they will be added to that coffee run. If they consumer has not previously been a part of any coffee runs, they will also be added to the coffee run history table. <br><br> Used when the type selected is `Drink`. |

The first argument must specify the datetime of the run to be edited. The second argument must specify the type of data to be edited. The arguments that follow will depend on the type editing selected.

##### Payer
The following is an example of editing the payer name to `Bob` for a run on 02/14/2024 at 12\:00\:00:
```
python coffee_run.py edit_run 02/14/2024 12:00:00 Payer Bob
```
##### Drink
The following is an example of editing the cost of Alice's drink to $4 for the run on 02/14/2024 at 12\:00\:00:
```
python coffee_run.py edit_run 02/14/2024 12:00:00 Drink Alice 4
```
Similarly, if Eve went to the coffee run on 02/14/2024 at 12\:00\:00 and got a $3.50 drink, but her drink was mistakenly not recorded, we can use:
```
python coffee_run.py edit_run 02/14/2024 12:00:00 Drink Eve 3.5
```

#### delete_run
```
delete_run <datetime>
```
| Argument | Description |
| --- | --- |
| `<datetime>` | The first argument must specify the datetime of the run to be deleted, formatted as `mm/dd/YYYY HH:MM:SS`. |

`delete_run` only takes the datetime of the run to be deleted. For example, to delete a data on the run from 02/14/2024 at 12\:00\:00:
```
python coffee_run.py delete_run 02/14/2024 12:00:00
```
