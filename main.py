from crossing_river import genetic_algorithm

print(genetic_algorithm(max_generations=50, numb_of_children=75, primary_pop_size=100,
                        mutation_rate=0.1, num_of_parents=50, mutation_probability=0.2, fitness_threshold=400))
