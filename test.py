# Define the Items array and the solution
Items = [
    {'id': 1, 'expiration_time': 3, 'value': 15, 'stock': 4, 'incompatible': [1, 10]},
    {'id': 2, 'expiration_time': 6, 'value': 10, 'stock': 2, 'incompatible': [4, 5]},
    {'id': 3, 'expiration_time': 5, 'value': 30, 'stock': 10, 'incompatible': []},
    {'id': 4, 'expiration_time': 4, 'value': 25, 'stock': 4, 'incompatible': [7]},
    {'id': 5, 'expiration_time': 9, 'value': 20, 'stock': 3, 'incompatible': [6]},
    {'id': 6, 'expiration_time': 1, 'value': 50, 'stock': 4, 'incompatible': [1]},
    {'id': 7, 'expiration_time': 7, 'value': 35, 'stock': 5, 'incompatible': [5, 10]},
    {'id': 8, 'expiration_time': 8, 'value': 25, 'stock': 1, 'incompatible': [1, 8]},
    {'id': 9, 'expiration_time': 5, 'value': 50, 'stock': 3, 'incompatible': [2, 3]},
    {'id': 10, 'expiration_time': 5, 'value': 20, 'stock': 5, 'incompatible': [1, 5]},
]

solution =[[6, 6], [9, 9], [4, 9], [7, 3], [7, 7], [7, 7], [5, 8], [5, 5], [], [], [], [], [], [], [], -60]
u=[[6, 6], [7, 9], [3, 3], [9, 9], [7, 7], [7, 7], [5, 5], [], [], [], [], [], [], [], [], -120]
r= [[6, 6], [9, 9], [3, 4], [9, 7], [7, 7], [7, 7], [5, 8], [5, 5], [], [], [], [], [], [], [], -60]
sample = [[6, 6], [9, 9], [3, 3], [7, 9], [7, 7], [7, 7], [5, 8], [5, 5], [], [], [], [], [], [], [], -50]

# Initialize variables for profit and loss
profit = 0
loss = 0

# Process each trip
for trip in solution[:-1]:  # Exclude the fitness value
    # Update expiration times and track transported items
    transported = []
    for item_id in trip:
        item = next(i for i in Items if i['id'] == item_id)
        if item['stock'] > 0 and item['expiration_time'] > 0:
            profit += item['value']
            item['stock'] -= 1
            transported.append(item_id)

    # Decrease expiration times for all items not transported
    for item in Items:
        if item['id'] not in transported:
            item['expiration_time'] -= 1

# Calculate losses for expired items
for item in Items:
    if item['stock'] > 0 and item['expiration_time'] <= 0:
        loss += item['stock'] * item['value']

# Calculate final fitness
fitness = profit - loss

# Return results
print(profit, loss, fitness)