import random

class defaults:
# Defult values so that the user doesnt have to explicidly
# state every feature of the genetic algorithm.
    def __init__(self):
        self.generations = 3
        self.chromosome_length = 4
        self.population_size = 5
        self.mutation_rate = 0.03

    def default_gene_function():
        return random.randint(1, 100)

    def default_fitness_function():
        pass

    def default_initialize_function():
        return random_initialization()

    def default_selection_function():
        return tournament_selection()

    def default_crossover_function():
        return fast_single_point_crossover()

    def default_mutations_function():
        return per_gene_mutation()

    def default_termination_point_function(amount):
        # The default termination point is based on how
        # many generations the user wants to run.
        return generation_termination(amount)

    def defult_get_highest_fitness():
        # Get the highest fitness of the current generation
        pass

    def default_get_lowest_fitness():
        # Get the lowest fitness of the current generation
        pass
