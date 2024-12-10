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
    # Add the first item if its in stock
    while 1:
        item1 = random.choice(items)
        if item1['stock'] != 0:
            trip.append(item1['id'])
            break

    # Add the second item if its in stock and compatible
    while 1:
        item2 = random.choice(items)
        if item2['stock'] != 0:
            if check_compatibility(item1['id'], item2['id']):
                trip.append(item2['id'])
                break
    return trip


# Check if the items are compatible in a trip
def check_compatibility(item1_id, item2_id):
    if item2_id in Items[item1_id - 1]['incompatible'] or item1_id in Items[item2_id - 1]['incompatible']:
        return False
    else:
        return True


# Generate a sample with random trip count
def generate_sample(items):
    num_trips = random.randint(1, 15)
    sample = []
    for _ in range(num_trips):
        trip = generate_trip(items)
        if updates_stocks(items, trip):
            sample.append(trip)
    decrement_expiration_times(items, num_trips)
    sample.extend([[-1, -1] for _ in range(15 - num_trips)])
    return sample


# Update expiration times
def decrement_expiration_times(items, num_trips):
    for item in items:
        item['expiration_time'] -= num_trips
        if item['expiration_time'] <= 0:
            item['stock'] = 0


# Update stocks
def updates_stocks(items, trip):
    for item_id in trip:
        item = next(item for item in items if item['id'] == item_id)
        if item['stock'] <= 0:
            return False
        item['stock'] -= 1
    return True


# Generate the primary population
def generate_population(size):
    population = []
    for _ in range(size):
        items = copy.deepcopy(Items)
        sample = generate_sample(items)
        sample.append(fitness(sample))
        population.append(sample)
    return population


# Fitness Function
def fitness(sample):
    items = copy.deepcopy(Items)
    decrement_expiration_times(items, len(sample))
    total_profit = 0

    for trip in sample:
        trip_profit = 0

        for item_id in trip:
            item = next(item for item in items if item['id'] == item_id)
            trip_profit += item['value']

        total_profit += trip_profit
    return total_profit


# Selection: Roulette Wheel
def select_population(population, number):
    values = [sample[-1] for sample in population]
    total_value = sum(values)
    probabilities = [v / total_value for v in values]

    # Select unique individuals
    selected = []
    candidates = random.choices(population, probabilities, k=number)
    for candidate in candidates:
        if candidate not in selected:
            selected.append(candidate)
    return selected


# Crossover: Single Point Crossover?
def crossover(parents):
    items = copy.deepcopy(Items)
    parent1, parent2 = random.choices(parents, k=2)

    point1 = 0
    point2 = 0
    while point2 == len(parent2) and point1 == 0:
        point1 = random.randint(0, len(parent1) - 1)
        point2 = random.randint(0, len(parent2))

    # Create offspring by combining segments from parents
    combination = parent1[:point1] + parent2[point2:]

    # Limit the trips to 8 and deleting the fitness value of parent
    combination = combination[:9]

    # Delete parent's fitness
    combination.pop()

    # Only keeping the trips that are valid in the sequence
    child = []
    for trip in combination:
        if updates_stocks(items, trip) and check_compatibility(trip[0], trip[1]):
            child.append(trip)

    # Add fitness value
    if child:
        value = fitness(child)
        child.append(value)
        return child
    return None


# Mutate a sample, mp = mutation probability
def mutate(sample, mp=0.05):
    # Removing fitness value
    sample.pop()

    items = copy.deepcopy(Items)
    for trip in sample:
        updates_stocks(items, trip)

    # Add Random deletion and insertion
    for i in range(len(sample)):
        if random.random() < mp:

            # Restore stocks
            for item_id in sample[i]:
                item = next(item for item in items if item['id'] == item_id)
                item['stock'] += 1

            # Generate a new trip
            sample[i] = generate_trip(items)

    # Recalculate fitness value
    sample.append(fitness(sample))

    return sample


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

    if len(similar_bests) >= 15:
        return True
    return False


# Driver function
def genetic_algorithm(max_generations, fitness_threshold, mutation_rate, numb_of_children,
                      primary_pop_size, num_of_parents, mutation_probability):
    # Creating the primary population
    primary_population = generate_population(primary_pop_size)

    similar_bests = []

    for generation in range(max_generations):

        parents = select_population(primary_population, num_of_parents)

        # Creating children
        children = []
        while numb_of_children > len(children):
            child = crossover(parents)
            if child:
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

        # Selection for survival: Select the top 2 samples to retain
        elite_samples = sorted(primary_population, key=lambda x: x[-1], reverse=True)[:1]
        selected_population = select_population(primary_population, primary_pop_size - len(elite_samples))
        primary_population = selected_population + elite_samples

        # Print and
        best_sample = max(primary_population, key=lambda x: x[-1])
        best_fitness = best_sample[-1]
        print(f"Best Fitness in Generation {generation + 1}: {best_fitness}\n Best sample is {best_sample}")

        # Check completion criteria
        # 1. Reaching Threshold
        if best_fitness >= fitness_threshold:
            print("Fitness threshold reached. Terminating.")
            return {"solution": best_sample, "fitness": best_fitness}
        # 2. No improvement for 15 consecutive generations
        elif detect_stagnation(similar_bests, best_sample):
            print("Solutions have Converged. Terminating.")
            return {"solution": best_sample, "fitness": best_fitness}

    # After all generations, return the best solution
    best_individual = max(primary_population, key=lambda x: x[-1])
    return {"solution": best_individual, "fitness": best_individual[-1]}


print(genetic_algorithm(max_generations=50, numb_of_children=200, primary_pop_size=200,
                        mutation_rate=0.5, num_of_parents=100, mutation_probability=0.2, fitness_threshold=400))
