
import json
import random
import math
from multiprocessing import Pool, cpu_count
from test_tool import get_results

def create_population(pop_size: int, grid_size=200):
    cell_size = (50000 / grid_size)**2
    drops_per_strategy = math.trunc(12500000 / cell_size)
    pop = []

    for _ in range(pop_size):
        remaining_drops = drops_per_strategy
        individual = {}
        t = 1

        while remaining_drops > 0:
            num_drops = random.randint(1, remaining_drops)
            drops = [[random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)]
                     for _ in range(num_drops)]
            individual[str(t)] = drops
            remaining_drops -= num_drops
            t += 1

        pop.append(individual)

    return pop

def mutation(individual, grid_size=200, mutation_rate=0.1):
    mutated = {t: [drop.copy() for drop in drops] for t, drops in individual.items()}

    for t in mutated:
        for i in range(len(mutated[t])):
            if random.random() < mutation_rate:
                choice = random.choice([0, 1])
                mutated[t][i][choice] = random.randint(0, grid_size-1)

    return mutated

def sp_crossover(parent1, parent2):
    child = {}
    timesteps = list(parent1.keys())
    crossover_point = random.randint(1, len(timesteps)-1)

    for i, t in enumerate(timesteps):
        if i < crossover_point:
            child[t] = [drop.copy() for drop in parent1[t]]
        else:
            child[t] = [drop.copy() for drop in parent2[t]]

    return child

def uniform_crossover(parent1, parent2):
    child = {}
    for t in parent1:
        child[t] = [random.choice([d1, d2]) for d1, d2 in zip(parent1[t], parent2[t])]
    return child


def eval_fitness(individual, num_iterations=500):
    time, _ = get_results(
        num_iterations=num_iterations,
        water_dropping_plan=individual
    )

    return time

def evaluate_population(population):
    with Pool(cpu_count()) as pool:
        fitness_scores = pool.map(eval_fitness, population)
    return fitness_scores

def tourny_selection(population, fitness_scores, k=3):
    k = min(k, len(population))
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
        fitness_scores = evaluate_population(population)

        selected = tourny_selection(population, fitness_scores)

        new_population = []
        for i in range(0, len(selected) - 1, 2):
            p1, p2 = selected[i], selected[i + 1]
            
            child1 = sp_crossover(p1, p2)
            child1 = mutation(child1)
            new_population.append(child1)

            child2 = sp_crossover(p2, p1)
            child2 = mutation(child2)
            new_population.append(child2)

        population = new_population

    fitness_scores = evaluate_population(population)
    best_idx = max(range(len(population)), key=lambda i: fitness_scores[i])
    best_plan = population[best_idx]

    print("Best plan:", best_plan)

    with open("population.json", "w") as f:
        json.dump(population, f, indent=2)
