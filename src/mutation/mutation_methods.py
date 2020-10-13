import random

class Mutation_Methods:

    class Population:
        """Methods for selecting chromosomes to mutate"""

        def random_selection(ga):
            """Selects random chromosomes"""

            # Loop through the population
            for index in range(ga.population.size()):

                # Randomly apply mutations
                if random.uniform(0, 1) < ga.mutation_rate:
                    ga.population.set_chromosome(ga.mutation_individual_impl(ga, ga.population.get_all_chromosomes()[index]), index)


    class Individual:
        """Methods for mutating a single chromosome"""

        def whole_chromosome(ga, chromosome):
            """Makes a completely random chromosome.
            Fills chromosome with new genes.
            """

            # Using the chromosome_impl to set every index inside of the chromosome
            if ga.chromosome_impl != None:
                return ga.make_chromosome([
                           ga.make_gene(ga.chromosome_impl(j))
                       for j in range(chromosome.size())])

            # Using the gene_impl
            elif ga.gene_impl != None:
                function = ga.gene_impl[0]
                return ga.make_chromosome([
                           ga.make_gene(function(*ga.gene_impl[1:]))
                       for j in range(chromosome.size())])

            # Exit because no gene creation method specified
            else:
                print("You did not specify any initialization constraints.")
                return None


        def single_gene(ga, chromosome):
            """Changes a random gene in the chromosome and resets the fitness."""
            chromosome.set_fitness(None)

            # Using the chromosome_impl
            if ga.chromosome_impl != None:
                index = random.randint(0, chromosome.size()-1)
                chromosome.set_gene(ga.make_gene(ga.chromosome_impl(index)), index)

            # Using the gene_impl
            elif ga.gene_impl != None:
                function = ga.gene_impl[0]
                index = random.randint(0, chromosome.size()-1)
                chromosome.set_gene(ga.make_gene(function(*ga.gene_impl[1:])), index)

            # Exit because no gene creation method specified
            else:
                print("You did not specify any initialization constraints.")

            return chromosome
