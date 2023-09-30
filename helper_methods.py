import pandas as pd
import numpy as np
import copy
import random

def read_portfolio(spreadsheet_name):
    df = pd.read_excel(spreadsheet_name)
    df_data = df.to_dict()
    data = {}
    index = 0
    for name in df_data["name"].values():
        data[name] = {'capacity': df_data["capacity"][index],
                      'variable_cost': df_data["variable_cost"][index],
                      'fixed_cost': df_data["fixed_cost"][index],
                      'fuel_cost': df_data["fuel_cost"][index],
                      "OM_variable_cost": df_data["OM_variable_cost"][index],
                      "plant_id": df_data["plant_id"][index],
                      "type": df_data["type"][index],
                      "portfolio_id": df_data["portfolio_id"][index],
                      "portfolio_name": df_data["portfolio_name"][index],
                      }

        index = index + 1

    return data

def read_demand(spreadsheet_name):

    df = pd.read_excel(spreadsheet_name)
    df_data = df.to_dict()
    demand = {}

    for round in [1, 2, 3, 4, 5, 6]:

        demand[round] = {}

        for hour in [1, 2, 3, 4]:

            demand[round][hour] = df_data["load"][(round-1)*4+(hour-1)]

    return demand

def read_bid_spreadsheet(spreadsheet_name):

    df = pd.read_excel(spreadsheet_name)
    data = df.to_dict()

    return data

def construct_bids_dict_for_one_hour(bids_table, hour):

    bids_dict = {}

    for index in bids_table["name"].keys():
        bids_dict[bids_table["name"][index]] = bids_table["Hour " +str(hour)][index]

    return bids_dict

def get_my_plants(id, data):

    plant_list = []

    for name in data.keys():

        if data[name]['portfolio_id'] == id:
            plant_list.append(name)

    return plant_list

def daily_fixed_costs(plant_names, data):

    fixed_cost = 0

    for name in plant_names:
        fixed_cost = fixed_cost + data[name]["fixed_cost"]

    return fixed_cost

def daily_records_to_csv(daily_records, plant_id):

    rent_incurred = []
    variable_cost_incurred = []
    fixed_cost_incurred = []
    daily_cash_flow = []
    interest = []
    change_from_prior_day = []
    new_balance = []

    for name in daily_records.keys():
        rent_incurred.append(daily_records[name]['rent_incurred'])
        variable_cost_incurred.append(daily_records[name]['variable_cost'])
        fixed_cost_incurred.append(daily_records[name]['fixed_cost'])
        daily_cash_flow.append(daily_records[name]['cash_flow'])
        interest.append(daily_records[name]['interest_payment'])
        change_from_prior_day.append(daily_records[name]['change_from_prior_day'])
        new_balance.append(daily_records[name]['new_balance'])

    df = pd.DataFrame(list(zip(rent_incurred,
                                variable_cost_incurred,
                                fixed_cost_incurred,
                                daily_cash_flow,
                                interest,
                                change_from_prior_day,
                                new_balance)),
                      columns=['rent_incurred',
                                'variable_cost',
                                'fixed_cost',
                                'cash_flow',
                                'interest_payment',
                                'change_from_prior_day',
                                'new_balance'])
    df.to_csv("Portfolio " +str(plant_id)+ " projected financial statement.csv")

def find_smallest(bids: np.ndarray) -> int:
    small_index = 0
    small = float('inf')

    l = len(bids)

    for i in range(l):
        temp = bids[i]
        if temp < small:
            small = temp
            small_index = i

    return small_index


def clear_market(bid_prices: np.ndarray, capacities: np.ndarray, demand_capacity: float) -> (np.ndarray, np.ndarray):
    unit_rent = np.zeros(42)
    unit_used_capacity = np.zeros(42)
    units_used = []
    total_capacity = 0
    # count = 0

    bid_prices_copy = copy.deepcopy(bid_prices)

    while total_capacity < demand_capacity:
        small_index = find_smallest(bid_prices_copy)
        smallest_bid = bid_prices_copy[small_index]

        # count = count+1
        # print(small_index)
        unit_used_capacity[small_index] = capacities[small_index]
        bid_prices_copy[small_index] = 2000
        total_capacity = total_capacity + capacities[small_index]

    marginal_price = smallest_bid
    unit_used_capacity[small_index] = capacities[small_index] - (total_capacity - demand_capacity)

    l = len(unit_rent)
    for i in range(l):
        if unit_used_capacity[i] != 0:
            unit_rent[i] = marginal_price * unit_used_capacity[i]

    return unit_rent, unit_used_capacity

# Finance module
def run_simulation(data, demand_data, bid_price_table, plant_id, my_plants, day_list, balance, save_results=False):
    daily_records = {}  # stores daily records about cash flow for our plants
    hourly_rent_capacity_records = {}  # stores hourly records about rent and capacity from every plant

    for current_day in day_list:

        rent_incurred = 0
        variable_costs_incurred = 0

        for hour in [1, 2, 3, 4]:

            mean_demand = demand_data[current_day][hour]

            demand = random.gauss(mean_demand, (0.03 * mean_demand))  # stochastic demand

            # Assume bid prices equivalent to variable costs
            bid_prices = construct_bids_dict_for_one_hour(bids_table=bid_price_table,
                                                          hour=((current_day - 1) * 4 + (hour - 1)))

            # Create lists for method output
            bid_price_list = []
            capacity_list = []

            for name in data.keys():

                bid_price_list.append(bid_prices[name])
                capacity_list.append(data[name]["capacity"])

            unit_rent_list, unit_used_capacity_list = clear_market(bid_price_list, capacity_list, demand)

            market_clearing_output = {}

            index = 0
            for name in data.keys():

                market_clearing_output[name] = {}

                market_clearing_output[name]['rent'] = unit_rent_list[index]
                market_clearing_output[name]['capacity'] = unit_used_capacity_list[index]

                index = index + 1

            hourly_rent_capacity_records[((current_day - 1) * 4 + (hour - 1))] = market_clearing_output

            for name in market_clearing_output.keys():

                if name in my_plants:
                    rent_incurred = rent_incurred + market_clearing_output[name]['rent']
                    variable_costs_incurred = variable_costs_incurred + market_clearing_output[name]['capacity'] * \
                                              data[name]["variable_cost"]

        # Calculate cash flow results, including debt calculation

        fixed_costs_incurred = daily_fixed_costs(my_plants, data)

        daily_cash_flow = rent_incurred - variable_costs_incurred - fixed_costs_incurred

        new_balance = balance + daily_cash_flow

        interest = 0

        if new_balance < 0:
            interest = -1 * new_balance * 0.05

            new_balance = new_balance - interest

        daily_records[current_day] = {

            "rent_incurred": rent_incurred,
            "variable_cost": variable_costs_incurred,
            "fixed_cost": fixed_costs_incurred,
            "cash_flow": daily_cash_flow,
            "interest_payment": interest,
            "change_from_prior_day": new_balance - balance,
            "new_balance": new_balance,
        }

        balance = new_balance

    if save_results == True:

        daily_records_to_csv(daily_records, plant_id)

    return balance


def binary_search(data, demand_data, bid_price_table, plant_id, my_plants, day_list,
              target_profit, epsilon, top_value, best_guess, bottom_value, mean_result, save_results=False):

    while (abs(target_profit - mean_result) > epsilon):

        stochastic_results = []

        for repetition in range(0, 10000):
            final_cash = run_simulation(data=data,
                                        demand_data=demand_data,
                                        bid_price_table=bid_price_table,
                                        plant_id=plant_id,
                                        my_plants=my_plants,
                                        day_list=day_list,
                                        balance=best_guess,
                                        save_results=save_results)

            stochastic_results.append(final_cash)

        mean_result = np.mean(stochastic_results)

        if mean_result > target_profit:

            # Need to pay less for asset
            top_value = best_guess
            best_guess = (best_guess + bottom_value) / 2

        else:

            # Need to pay more for asset
            bottom_value = best_guess
            best_guess = (best_guess + top_value) / 2

        print("\nPurchase price: " +str(-best_guess))
        print("Expected Profit: " +str(mean_result))

    return -best_guess
