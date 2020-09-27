import random
# Import all the data prebuilt modules
from initialization.population_structure.population import population as create_population
from initialization.chromosome_structure.chromosome import chromosome as create_chromosome
from initialization.gene_structure.gene import gene as create_gene

# Import functionality defaults
from initialization.random_initialization import random_initialization


class GA:
    def __init__(self):
        # Default variables
        self.chromosome_impl = None
        self.gene_impl = None
        self.population = None
        self.current_generation = 0
        self.generations = 3
        self.chromosome_length = 3
        self.population_size = 5
        self.mutation_rate = 0.03
        # Defualt EastGA implimentation structure
        self.initialization_impl = random_initialization
        self.update_fitness = True
        #self.mutation_impl = PerGeneMutation(Mutation_rate)
        #self.selection_impl = TournamentSelection()
        #self.crossover_impl = FastSinglePointCrossover()
        #self.termination_impl = GenerationTermination(Total_generations)
        #self.evaluation_impl = TestEvaluation()

    def initialize(self):
        self.population = self.initialization_impl(
        self.population_size,
        self.chromosome_length,
        self.chromosome_impl,
        self.gene_impl)
    
    def fitness_impl(self, chromosome):
        """Returns the fitness of a chromosome"""
        pass
    
    def evolve(self):
        """Updates the ga to the next generation.
        If update_fitness is set then all fitness values are updated.
        Otherwise only fitness values set to None (i.e. uninitialized fitness values) are updated."""
        for chromosome in self.population.get_all_chromosomes():
            if self.update_fitness or chromosome.get_fitness() is None:
                chromosome.set_fitness(self.fitness_impl(chromosome))
    
    def active(self):
        """Returns if the ga should terminate or not"""
        return self.current_generation < self.generations

    def evolve_generation(self, number_of_generations):
        # If you want to evolve through a number of generations
        # and be able to pause and output data based on that generation run.
        pass

    def make_gene(self,value):
        return create_gene(value)

    def make_chromosome(self):
        return create_chromosome()

    def make_population(self):
        return create_population()
