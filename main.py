from crossing_river import genetic_algorithm

print(genetic_algorithm(max_generations=100, numb_of_children=200, primary_pop_size=200,
                        mutation_rate=0.6, num_of_parents=100, mutation_probability=0.2))