
import random
import math

from test_tool import get_results

def create_population(pop_size: int, grid_size=200):
    cell_size = (50000 / grid_size)**2
    drops_per_strategy = math.trunc(12500 / cell_size)
    pop = []

    for _ in range(pop_size):
        individual = []
        for t in range(drops_per_strategy):
            x = random.randint(0, grid_size-1)
            y = random.randint(0, grid_size-1)
            individual.append((t, x, y))
        pop.append(individual)
    
    return pop

def mutation(individual, grid_size=200, mutation_rate=0.1):
    mutated = individual.copy()
    num_mutations = max(1, int(len(individual) * mutation_rate))

    for _ in range(num_mutations):
        idx = random.randint(0, len(individual) - 1)
        t, x, y = mutated[idx]

        choice = random.choice(['x', 'y', 't'])
        if choice == 'x':
            x = random.randint(0, grid_size - 1)
        elif choice == 'y':
            y = random.randint(0, grid_size - 1)
        elif choice == 't':
            t = max(0, t + random.randint(-1, 1))

        mutated[idx] = (t, x, y)
    
    return mutated

def sp_crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child = parent1[:crossover_point] + parent2[crossover_point:]
    return child

def uniform_crossover(parent1, parent2):
    child = []
    for drop1, drop2 in zip(parent1, parent2):
        child.append(random.choice([drop1, drop2]))
    return child

def eval_fitness(individual, num_iterations=500):
    time, _ = get_results(
        num_iterations=num_iterations,
        water_dropping_plan=individual
    )

    return time

def tourny_selection(population, fitness_scores, k=3):
    selected = []
    for _ in range(len(population)):
        competitors = random.sample(list(zip(population, fitness_scores)), k)
    
        winner = max(competitors, key=lambda x: x[1])[0]
        selected.append(winner)
    return selected

if __name__ == "__main__":
    population = create_population(pop_size=20, grid_size=200)
    num_generations = 50

    for gen in range(num_generations):
        fitness_scores = [eval_fitness(ind) for ind in population]

        selected = tourny_selection(population, fitness_scores)

        new_population = []
        for i in range(0, len(selected), 2):
            p1, p2 = selected[i], selected[i + 1]
            
            # Change
            child = sp_crossover(p1, p2)
            child = mutation(child)
            new_population.append(child)

        population = new_population

    best_idx = max(range(len(population)), key=lambda i: eval_fitness(population[i]))
    best_plan = population[best_idx]

    print(best_plan)

