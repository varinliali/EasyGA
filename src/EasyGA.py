# Import all the data structure prebuilt modules
from structure import Population as create_population
from structure import Chromosome as create_chromosome
from structure import Gene as create_gene

# Structure Methods
from fitness_function  import Fitness_Examples
from initialization    import Initialization_Methods
from termination_point import Termination_Methods

# Parent/Survivor Selection Methods
from parent_selection   import Parent_Selection
from survivor_selection import Survivor_Selection

# Genetic Operator Methods
from mutation  import Mutation_Methods
from crossover import Crossover_Methods

# Default Attributes for the GA
from attributes import Attributes

# Database class
from database import sql_database
from sqlite3  import Error

# Graphing package
from database import matplotlib_graph
import matplotlib.pyplot as plt


class GA(Attributes):
    """GA is the main class in EasyGA. Everything is run through the ga
    class. The GA class inherites all the default ga attributes from the
    attributes class.

    An extensive wiki going over all major functions can be found at
    https://github.com/danielwilczak101/EasyGA/wiki
    """


    def evolve_generation(self, number_of_generations = 1, consider_termination = True):
        """Evolves the ga the specified number of generations."""

        cond1 = lambda: number_of_generations > 0  # Evolve the specified number of generations.
        cond2 = lambda: not consider_termination   # If consider_termination flag is set:
        cond3 = lambda: cond2() or self.active()   #     check termination conditions.

        while cond1() and cond3():

            # Create the initial population if necessary.
            if self.population is None:
                self.initialize_population()

            # If its the first generation, setup the database.
            if self.current_generation == 0:

                # Create the database here to allow the user to change the
                # database name and structure before running the function.
                self.database.create_all_tables(self)

                # Add the current configuration to the config table
                self.database.insert_config(self)

            # Otherwise evolve the population.
            else:
                self.parent_selection_impl(self)
                self.crossover_population_impl(self)
                self.survivor_selection_impl(self)
                self.population.update()
                self.mutation_population_impl(self)

            # Update and sort fitnesses
            self.set_all_fitness()
            self.population.sort_by_best_fitness(self)

            # Save the population to the database
            self.save_population()

            number_of_generations -= 1
            self.current_generation += 1

        self.adapt()


    def evolve(self, number_of_generations = 1, consider_termination = True):
        """Runs the ga until the termination point has been satisfied."""

        while self.active():
            self.evolve_generation(number_of_generations, consider_termination)


    def active(self):
        """Returns if the ga should terminate based on the termination implimented."""

        return self.termination_impl(self)


    def adapt(self):
        """Modifies the parent ratio and mutation rates
        based on the adapt rate and percent converged.
        Attempts to balance out so that a portion of the
        population gradually approaches the solution.

        Afterwards also heavily crosses the worst chromosomes
        with the best chromosome, depending on how well the
        overall population is doing.
        """

        # Don't adapt
        if self.adapt_rate is None or self.adapt_rate <= 0:
            return

        # Amount of the population desired to converge (default 50%)
        amount_converged = round(self.percent_converged*len(self.population))

        # How much converged halfway
        best_fitness = self.population[0].fitness
        threshhold_fitness = self.population[amount_converged//2].fitness

        # Closeness required for convergence
        tol_half = abs(best_fitness - threshhold_fitness)/2

        # How much converged a quarter of the way
        threshhold_fitness = self.population[amount_converged//4].fitness

        # Tolerance result
        tol_quar = abs(best_fitness - threshhold_fitness)

        # Change rates with:
        multiplier = 1 + self.adapt_rate

        # Minimum and maximum mutation rates
        min_rate = 0.05
        max_rate = 0.25

        # Adapt twice as fast if it's really bad
        if tol_quar < tol_half/2 or tol_quar > tol_half*2:
            multiplier **= 2

        # Too few converged: cross more and mutate less
        if tol_quar > tol_half:

            self.selection_probability    = min(0.75    , self.selection_probability    * multiplier)
            self.chromosome_mutation_rate = max(min_rate, self.chromosome_mutation_rate / multiplier)
            self.gene_mutation_rate       = max(min_rate, self.gene_mutation_rate       / multiplier)

        # Too many converged: cross less and mutate more
        else:

            self.selection_probability    = max(0.25    , self.selection_probability    / multiplier)
            self.chromosome_mutation_rate = min(max_rate, self.chromosome_mutation_rate * multiplier)
            self.gene_mutation_rate       = min(max_rate, self.gene_mutation_rate       * multiplier)

        # Strongly cross the best chromosome with the worst chromosomes
        for n in range(1, amount_converged//4):
            self.population[-n] = self.crossover_individual_impl(
                self,
                self.population[-n],
                self.population[0],
                min(0.5, tol_half)
            )
            self.population[-n].fitness = self.fitness_function_impl(self.population[-n])

        self.population.sort_by_best_fitness(self)


    def initialize_population(self):
        """Initialize the population using
        the initialization implimentation
        that is currently set.
        """

        self.population = self.initialization_impl(self)


    def set_all_fitness(self):
        """Will get and set the fitness of each chromosome in the population.
        If update_fitness is set then all fitness values are updated.
        Otherwise only fitness values set to None (i.e. uninitialized
        fitness values) are updated.
        """

        # Check each chromosome
        for chromosome in self.population:

            # Update fitness if needed or asked by the user
            if chromosome.fitness is None or self.update_fitness:
                chromosome.fitness = self.fitness_function_impl(chromosome)


    def sort_by_best_fitness(self, chromosome_list, in_place = False):
        """Sorts the chromosome list by fitness based on fitness type.
        1st element has best fitness.
        2nd element has second best fitness.
        etc.
        """

        if in_place:
            return chromosome_list.sort(                       # list to be sorted
                key = lambda chromosome: chromosome.fitness,   # by fitness
                reverse = (self.target_fitness_type == 'max')  # ordered by fitness type
            )

        else:
            return sorted(
                chromosome_list,                               # list to be sorted
                key = lambda chromosome: chromosome.fitness,   # by fitness
                reverse = (self.target_fitness_type == 'max')  # ordered by fitness type
            )


    def get_chromosome_fitness(self, index):
        """Returns the fitness value of the chromosome
        at the specified index after conversion based
        on the target fitness type.
        """

        return self.convert_fitness(
            self.population[index].fitness
        )


    def convert_fitness(self, fitness_value):
        """Returns the fitness value if the type of problem
        is a maximization problem. Otherwise the fitness is
        inverted using max - value + min.
        """

        # No conversion needed
        if self.target_fitness_type == 'max': return fitness_value

        max_fitness = self.population[-1].fitness
        min_fitness = self.population[0].fitness

        # Avoid catastrophic cancellation
        if min_fitness / max_fitness < 1e-5:
            return -fitness_value

        # Otherwise flip values
        else:
            return max_fitness - fitness_value + min_fitness


    def print_generation(self):
        """Prints the current generation"""
        print(f"Current Generation \t: {self.current_generation}")


    def print_population(self):
        """Prints the entire population"""
        print(self.population)


    def print_best_chromosome(self):
        """Prints the best chromosome and its fitness"""
        print(f"Best Chromosome \t: {self.population[0]}")
        print(f"Best Fitness    \t: {self.population[0].fitness}")


    def print_worst_chromosome(self):
        """Prints the worst chromosome and its fitness"""
        print(f"Worst Chromosome \t: {self.population[-1]}")
        print(f"Worst Fitness    \t: {self.population[-1].fitness}")
