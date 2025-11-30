
import json
import random
import math
from multiprocessing import Pool, cpu_count
from test_tool import get_results

def predict_fire_position(
    t,
    total_steps=250,
    start_x=0,
    end_x=180,
    firefront_min_y=0,
    firefront_max_y=80
):
    alpha = t / total_steps
    xf = start_x + alpha * (end_x - start_x)

    yf = random.uniform(firefront_min_y, firefront_max_y)
    return xf, yf

def make_strip_near_fire(t, max_x=200, max_y=80):
    xf, yf = predict_fire_position(t)

    offset_x = random.randint(-8, 20)
    offset_y = random.randint(-8, 8)

    cx = int(max(0, min(max_x, xf + offset_x)))
    cy = int(max(0, min(max_y, yf + offset_y)))

    y1 = max(0, min(max_y, cy - 5))
    y2 = max(0, min(max_y, cy + 5))
    x1 = x2 = cx

    return [ [int(x1), int(y1)], [int(x2), int(y2)] ]

def generate_plan():
    chosen = sorted(random.sample(range(250), k=20))
    plan = {}
    for t in chosen:
        plan[str(t)] = make_strip_near_fire(t)
    return plan

def generate_and_save_one_plan(path="one_plan.json"):
    plan = generate_plan()
    with open(path, "w") as f:
        json.dump(plan, f, indent=2)
    return plan

def generate_many_plans(n=30):
    return [generate_plan() for _ in range(n)]

def mutate_plan(plan, mutation_rate=1.0):
    new_plan = dict(plan)

    num_mutations = max(1, int(mutation_rate))

    for _ in range(num_mutations):
        remove_key = random.choice(list(new_plan.keys()))
        del new_plan[remove_key]

        all_steps = set(range(250))
        used_steps = set(map(int, new_plan.keys()))
        free_steps = list(all_steps - used_steps)

        if not free_steps:
            continue

        new_timestep = random.choice(free_steps)
        new_plan[str(new_timestep)] = make_strip_near_fire(new_timestep)

    return new_plan

def sp_crossover(parent1, parent2):
    p1 = sorted(parent1.items(), key=lambda x: int(x[0]))
    p2 = sorted(parent2.items(), key=lambda x: int(x[0]))

    cx = random.randint(1, len(p1) - 1)

    head = p1[:cx]
    tail = p2[cx:]

    merged = head + tail

    child = {}
    used_steps = set()

    for t_str, strip in merged:
        t = int(t_str)
        if t not in used_steps:
            child[str(t)] = strip
            used_steps.add(t)

    while len(child) < 20:
        all_steps = set(range(250))
        free_steps = list(all_steps - used_steps)
        t_new = random.choice(free_steps)
        child[str(t_new)] = make_strip_near_fire(t_new)
        used_steps.add(t_new)

    return child

def eval_fitness(individual, num_iterations=500):
    time = get_results(
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

def load_population(path):
    with open(path, "r") as f:
        data = json.load(f)

    cleaned = []
    for idx, individual in enumerate(data):
        indiv_clean = {str(t): drops for t, drops in individual.items()}
        cleaned.append(indiv_clean)

        timestep_counts = {t: len(drops) for t, drops in indiv_clean.items()}
        total_drops = sum(timestep_counts.values())

        print(f"Plan {idx+1}:")
        print(f"  Timesteps: {len(indiv_clean)}")
        print(f"  Drops per timestep: {timestep_counts}")
        print(f"  Total drops: {total_drops}")
        print("-" * 40)

    print(f"Total plans loaded: {len(cleaned)}")
    return cleaned

def ea():
    population = generate_many_plans()
    num_generations = 50
    pop_size = len(population)
    elite_count = 2
    cx_prob = 0.9
    mut_prob = 0.2   

    for gen in range(num_generations):
        fitness_scores = evaluate_population(population)

        avg_fit = sum(fitness_scores) / len(fitness_scores)
        print(f"----- Generation {gen} | Avg Fitness: {avg_fit:.3f} -----")

        elites = [
            ind for ind, fit in sorted(
                zip(population, fitness_scores),
                key=lambda x: x[1],
                reverse=True
            )[:elite_count]
        ]

        selected = tourny_selection(population, fitness_scores)

        new_population = elites.copy()
        while len(new_population) < pop_size:
            p1, p2 = random.sample(selected, 2)
            
            if random.random() < cx_prob:
                child1 = sp_crossover(p1, p2)
            else:
                child1 = p1.copy()

            if random.random() < mut_prob:
                child1 = mutate_plan(child1)

            new_population.append(child1)

            if len(new_population) >= pop_size:
                break

            if random.random() < cx_prob:
                child2 = sp_crossover(p2, p1)
            else:
                child2 = p2.copy()

            if random.random() < mut_prob:
                child2 = mutate_plan(child2)

            new_population.append(child2)

        population = new_population

    fitness_scores = evaluate_population(population)
    best_idx = max(range(len(population)), key=lambda i: fitness_scores[i])
    best_plan = population[best_idx]

    print("Best plan:", best_plan)

    with open("/src/output/population_1.json", "w") as f:
        json.dump(population, f, indent=2)

if __name__ == "__main__":
    ea()
