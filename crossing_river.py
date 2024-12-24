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
    # Generate trips for sample
    for i in range(15):
        trip = generate_trip(items)
        if trip and update_stocks(items, trip):
            sample.append(trip)
        update_expirations(items)

    # Normalize the sample
    remaining_trips = 15 - len(sample)
    sample.extend([[] for _ in range(remaining_trips)])

    # Calculate fitness
    sample.append(fitness(sample))

    return sample


# Decrease expiration time
def update_expirations(items):
    total_loss = 0
    for item in items:
        if item['stock'] > 0:
            item['expiration_time'] -= 1
            if item['expiration_time'] <= 1:
                item['stock'] = 0


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
def fitness(sample):
    fitness_value = sum(i['value'] * i['stock'] for i in Items)

    for trip in sample:
        if trip:
            for item_id in trip:
                item = next(item for item in Items if item_id == item['id'])
                fitness_value = fitness_value - item['value'] * 2

    return - fitness_value


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
    valid_trips = []
    # Only keeping the trips that are valid in the sequence
    for trip in trips:
        if trip:
            if valid_trip(items, trip):
                valid_trips.append(trip)
                update_expirations(items)

    # Normalize the sample
    remaining_trips = 15 - len(valid_trips)
    valid_trips.extend([[] for _ in range(remaining_trips)])

    # Add fitness value
    valid_trips.append(fitness(valid_trips))

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
def calculate_mr(mr_controller, mr, max_generations):
    return max(0.05, mr * (1 - (mr_controller / max_generations)))


# Detect stagnation
def detect_stagnation(similar_bests, best_sample, threshold=10):
    # Store the best sample in each generation if it's the same as last generation
    if similar_bests:
        if similar_bests[-1] == best_sample:
            similar_bests.append(best_sample)
        else:
            similar_bests.clear()
    else:
        similar_bests.append(best_sample)

    if len(similar_bests) >= threshold:
        return True
    return False


# Driver function
def genetic_algorithm(max_generations, mutation_rate, numb_of_children,
                      primary_pop_size, num_of_parents, mutation_probability):
    # Creating the primary population
    best_sample = []
    primary_population = generate_population(primary_pop_size)

    # Initialize controller variables
    similar_bests = []
    termination_enable = False
    first_mr = mutation_rate
    mr_controller = 0
    
    for generation in range(max_generations):
            
        #print(f"Mutation Rate: {mutation_rate}, first: {first_mr}")
        parents = select_population(primary_population, num_of_parents)

        # Creating children
        children = []
        while numb_of_children > len(children):
            child = crossover(parents)
            children.append(child)

        # Mutation on children
        mutation_list = []
        mutation_rate = calculate_mr(mr_controller, mutation_rate, max_generations)
        mr_controller += 1
        for sample in children:
            if random.randint(1, 100) > mutation_rate * 100:
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
        print(f"Best Fitness in Generation {generation + 1}: {best_sample[-1]}\n Best sample is {best_sample}")

        # Detect stagnation
        if detect_stagnation(similar_bests, best_sample, 10):
            if termination_enable:
                print("Solutions have Converged. Terminating")
                break
               
            else:
                print("Solutions have Converged. Resetting mutation rate")
                mutation_rate = first_mr
                mr_controller = 0
                similar_bests.clear()
                termination_enable = True

    # After all generations, return the best solution
    return {"solution": best_sample, "fitness": best_sample[-1]}

