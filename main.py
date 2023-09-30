from helper_methods import *

data = read_portfolio('portfolios.xlsx')
demand_data = read_demand("Supply_and_demand_curves.xlsx")
bid_price_table = read_bid_spreadsheet("Bid_Prices.xlsx")

# Variables for simulation
plant_id = 7 # Trial with Fossil_Light
# starting_balance = -61500 # Trial with East_Bay
day_list = [1, 2, 3, 4, 5, 6]
my_plants = get_my_plants(plant_id, data)

# Variables for binary search
target_profit = 71805.92
epsilon = 500 # If ( |binary_search_guess-target_profit| < epsilon), the binary search will halt

# Binary Search Module
top_value = 0
best_guess = -500000
bottom_value = -1000000
mean_result = 0

purchase_price = binary_search(data, demand_data, bid_price_table, plant_id, my_plants, day_list,
              target_profit, epsilon, top_value, best_guess, bottom_value, mean_result, save_results=False)

print("Maximum suggested bid: " + str(purchase_price))



