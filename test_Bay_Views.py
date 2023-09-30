from helper_methods import *

data = read_portfolio('portfolios.xlsx')
demand_data = read_demand("Supply_and_demand_curves.xlsx")
bid_price_table = read_bid_spreadsheet("Bid_Prices.xlsx")

# Variables for simulation
plant_id = 4 # Trial with East_Bay
starting_balance = -2000 # Trial with East_Bay
day_list = [1, 2, 3, 4, 5, 6]
my_plants = get_my_plants(plant_id, data)

stochastic_results = []

for repetition in range(0, 10000):
    final_cash = run_simulation(data=data,
                                demand_data=demand_data,
                                bid_price_table=bid_price_table,
                                plant_id=plant_id,
                                my_plants=my_plants,
                                day_list=day_list,
                                balance=starting_balance,
                                save_results=True)

    stochastic_results.append(final_cash)

print(stochastic_results)
print(np.var(stochastic_results))

expected_profit = np.mean(stochastic_results)

print("Expected profit: " + str(expected_profit))