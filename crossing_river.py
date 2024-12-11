import copy
import random

# List of all goods
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


# Generate a trip with 2 items
def generate_trip(items):
    trip = []
    # Filter items in stock
    available_items = [item for item in items if item['stock'] > 0]

    # Return empty trip if no item is available
    if not available_items:
        return trip

    # Select first item
    item1 = random.choice(available_items)
    trip = [item1['id']]

    # Select compatible second item
    available_items = [item for item in available_items if check_compatibility(item1['id'], item['id'])]
    if available_items:
        item2 = random.choice(available_items)
        trip.append(item2['id'])

    return trip


# Check if the items in a trip are compatible
def check_compatibility(item1_id, item2_id):
    item1 = next(item for item in Items if item['id'] == item1_id)
    item2 = next(item for item in Items if item['id'] == item2_id)
    return item2_id not in item1['incompatible'] and item1_id not in item2['incompatible']


# Generate a sample with random trip count
def generate_sample(items):
    sample = []
    total_loss = 0

    # Generate trips for sample
    for i in range(15):
        trip = generate_trip(items)
        if trip and update_stocks(items, trip):
            sample.append(trip)
        total_loss += calculate_loss(items)

    # Normalize the sample
    remaining_trips = 15 - len(sample)
    sample.extend([[] for _ in range(remaining_trips)])

    # Calculate fitness
    total_loss += sum(calculate_loss(items) for _ in range(remaining_trips))
    sample.append(total_loss)
    sample[-1] = fitness(sample, items)

    return sample


# Calculate the loss caused by expiration
def calculate_loss(items):
    total_loss = 0
    for item in items:
        if item['stock'] > 0:
            item['expiration_time'] -= 1
            if item['expiration_time'] <= 1:
                total_loss += item['stock'] * item['value']
                item['stock'] = 0
    return total_loss


# Update stocks and check if a trip's items are in stock
def update_stocks(items, trip):
    for item_id in trip:
        item = next(item for item in items if item['id'] == item_id)
        if item['stock'] == 0:
            return False
        item['stock'] -= 1
    return True


# Generate population
def generate_population(size):
    population = []
    for _ in range(size):
        items = copy.deepcopy(Items)
        sample = generate_sample(items)
        population.append(sample)
    return population


# Fitness Function
def fitness(sample, items):
    total_profit = 0
    total_loss = sample[-1]

    for trip in sample[:-1]:
        if not trip:
            pass

        # Add all the transported items values
        trip_profit = 0
        for item_id in trip:
            item = next(item for item in items if item['id'] == item_id)
            trip_profit += item['value']
        total_profit += trip_profit

    # Add profit and loss
    return total_profit - total_loss


# Selection: Roulette Wheel
def select_population(population, num):
    # Calculate fitness values
    fitness_values = [sample[-1] for sample in population]
    min_fitness = min(fitness_values)
    normalized_fitness = [f - min_fitness + 1 for f in fitness_values]

    # Calculate probabilities
    fitness_sum = sum(normalized_fitness)
    probabilities = [f / fitness_sum for f in normalized_fitness]

    # Select samples
    selected_unique = []
    selected = random.choices(population, probabilities, k=num)
    selected_unique = [sample for sample in selected if sample not in selected_unique]

    return selected_unique


# Crossover: Uniform Crossover
def crossover(parents):
    parent1, parent2 = random.sample(parents, k=2)
    child = []
    # Create offspring by combining segments from parents
    for i in range(15):
        if random.randint(0, 1):
            child.append(parent1[i])
        else:
            child.append(parent2[i])
    # Delete parent's fitness
    child.pop()

    return validate_sample(child, copy.deepcopy(Items))


# Trip validation
def valid_trip(items, trip):
    if len(trip) == 2:
        return update_stocks(items, trip) and check_compatibility(trip[0], trip[1])
    return update_stocks(items, trip)


#  Normalize and validate Sample
def validate_sample(trips, items):
    total_loss = 0
    valid_trips = []
    # Only keeping the trips that are valid in the sequence
    for trip in trips:
        if trip:
            if valid_trip(items, trip):
                valid_trips.append(trip)
                total_loss += calculate_loss(items)

    # Normalize the sample
    remaining_trips = 15 - len(valid_trips)
    valid_trips.extend([[] for _ in range(remaining_trips)])

    # Calculate loss
    total_loss += sum(calculate_loss(items) for _ in range(remaining_trips))
    valid_trips.append(total_loss)

    # Add fitness value
    valid_trips[-1] = fitness(valid_trips, items)

    return valid_trips


# Mutate a sample, mp = mutation probability
def mutate(sample, mp=0.05):
    # Removing fitness value
    sample.pop()
    items = copy.deepcopy(Items)
    mutated_sample = []

    # Mutate
    for trip in sample:
        if random.random() < mp:
            mutated_sample.append(generate_trip(items))
        else:
            if trip:
                mutated_sample.append(trip)

    # Normalize and Validate
    return validate_sample(mutated_sample, items)


# Calculate mr to decrease over generations
def calculate_mr(generation, mr, max_generations):
    return max(0.05, mr * (1 - (generation / max_generations)))


# Detect stagnation
def detect_stagnation(similar_bests, best_sample):
    # Store the best sample in each generation if it's the same as last generation
    if similar_bests:
        if similar_bests[-1] == best_sample:
            similar_bests.append(best_sample)
        else:
            similar_bests.clear()
    else:
        similar_bests.append(best_sample)

    if len(similar_bests) >= 20:
        return True
    return False


# Driver function
def genetic_algorithm(max_generations, mutation_rate, numb_of_children,
                      primary_pop_size, num_of_parents, mutation_probability):
    # Creating the primary population
    primary_population = generate_population(primary_pop_size)

    similar_bests = []

    reset_counter = 10

    for generation in range(max_generations):
        parents = select_population(primary_population, num_of_parents)

        # Creating children
        children = []
        while numb_of_children > len(children):
            child = crossover(parents)
            children.append(child)

        # Mutation on children
        mutation_list = []
        for sample in children:
            if random.randint(1, 100) > calculate_mr(generation, mutation_rate, max_generations) * 100:
                mutation_list.append(sample)
        children = [sample for sample in children if sample not in mutation_list]
        for sample in mutation_list:
            children.append(mutate(sample, mutation_probability))

        # Add children to population
        primary_population.extend(children)

        # Selection for survival: Select the top 3 samples to retain
        elite_samples = sorted(primary_population, key=lambda x: x[-1], reverse=True)[:3]
        selected_population = select_population(primary_population, primary_pop_size - len(elite_samples))
        primary_population = selected_population + elite_samples

        # Find the best sample in generation
        best_sample = max(primary_population, key=lambda x: x[-1])
        # best_fitness = best_sample[-1]
        # print(f"Best Fitness in Generation {generation + 1}: {best_fitness}\n Best sample is {best_sample}")

        # Wait for 20 generations before resetting population again
        if reset_counter < 20:
            reset_counter += 1
        else:
            # Detect stagnation
            if detect_stagnation(similar_bests, best_sample):
                print("Solutions have Converged. Resetting population")
                reset_population = generate_population(len(primary_population) // 2)
                primary_population = reset_population + elite_samples
                reset_counter = 0

    # After all generations, return the best solution
    best_individual = max(primary_population, key=lambda x: x[-1])
    return {"solution": best_individual, "fitness": best_individual[-1]}


print(genetic_algorithm(max_generations=100, numb_of_children=200, primary_pop_size=400,
                        mutation_rate=0.5, num_of_parents=200, mutation_probability=0.1))
