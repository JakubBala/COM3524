
import json
import random
from multiprocessing import Pool, cpu_count
from test_tool import get_results

"""
This is the code for the evolutionary algorithm. We tried running it a few times
with greater restriction each time, and it seemed to learn something. But, due to
the randomness of the fire spread, and the overwhelming no. of strips of water 
possible, it was not as effective as dropping water where we though was best.

If we had more time and better computing power, we think it would be a good
strategy. More work would need to be added to model the practical possibilities
of aerial firefighting - how quickly a plane could get to the location, and etc.
"""

def predict_fire_position(
    t,
    total_steps=250,
    start_x=0,
    end_x=180
):
    # Used to restrict population to more useful individuals
    progression = t / total_steps
    x_prediction = start_x + progression * (end_x - start_x)

    return x_prediction

def make_strip_near_fire(t, max_x=200, max_y=80):
    x_predicted = predict_fire_position(t)

    # More random offset
    offset_x = random.randint(-8, 20)
    y_random = random.randint(0, 80)

    centre_x = int(max(0, min(max_x, x_predicted + offset_x)))
    centre_y = int(max(0, min(max_y,y_random)))

    # Horizontal only (x and y are reversed)
    y1 = max(0, min(max_y, centre_y - 5))
    y2 = max(0, min(max_y, centre_y + 5))
    x1 = x2 = centre_x

    return [ [x1, y1], [x2, y2] ]

def generate_plan():
    # Sample 20 ts, because 20 * 10 = 12,500,000 / (250 * 250)
    # i.e., 20 strips of 10 equals the total area of water we can drop
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
    # Population
    return [generate_plan() for _ in range(n)]

def mutate_plan(plan, mutation_rate=1.0):
    # Remove random strip of water, add another
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

    merged = p1[:cx] + p2[cx:]

    child = {}
    used_steps = set()

    for t_str, strip in merged:
        t = int(t_str)
        if t not in used_steps:
            child[str(t)] = strip
            used_steps.add(t)

    # Make sure child is the right length
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
    # It takes a long time to run, so we use parallelisation
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
    # Used to continue running after some num generations because it takes so long.
    with open(path, "r") as f:
        data = json.load(f)

    cleaned = []
    for idx, individual in enumerate(data):
        indiv_clean = {str(t): drops for t, drops in individual.items()}
        cleaned.append(indiv_clean)

        timestep_counts = {t: len(drops) for t, drops in indiv_clean.items()}
        total_drops = sum(timestep_counts.values())

        print(f"Plan {idx+1}:   Total drops: {total_drops}")

    return cleaned

def ea():
    population = generate_many_plans()
    num_generations = 50
    pop_size = len(population)

    # Use elitism, probabilistic crossover and mutation
    elite_count = 2
    cx_prob = 0.9
    mut_prob = 0.2   

    for gen in range(num_generations):
        fitness_scores = evaluate_population(population)

        # Check progress
        avg_fit = sum(fitness_scores) / len(fitness_scores)
        print(f"Generation {gen}, Avg Fitness: {avg_fit:.3f}")

        # Make sure we carry over the best
        elites = [
            ind for ind, _ in sorted(
                zip(population, fitness_scores),
                key=lambda x: x[1],
                reverse=True
            )[:elite_count]
        ]

        selected = tourny_selection(population, fitness_scores)

        new_population = elites.copy()
        while len(new_population) < pop_size:
            p1, p2 = random.sample(selected, 2)
            
            # 2 children to maintain pop size
            if random.random() < cx_prob:
                child1 = sp_crossover(p1, p2)
            else:
                child1 = p1.copy()

            if random.random() < mut_prob:
                child1 = mutate_plan(child1)

            if len(new_population) >= pop_size:
                break

            if random.random() < cx_prob:
                child2 = sp_crossover(p2, p1)
            else:
                child2 = p2.copy()

            if random.random() < mut_prob:
                child2 = mutate_plan(child2)

            new_population.append(child1)
            new_population.append(child2)

        population = new_population

    fitness_scores = evaluate_population(population)
    best_idx = max(range(len(population)), key=lambda i: fitness_scores[i])
    best_plan = population[best_idx]

    print(f"Best plan: {best_plan}")

    with open("/src/output/population_1.json", "w") as f:
        json.dump(population, f, indent=2)

if __name__ == "__main__":
    ea()
