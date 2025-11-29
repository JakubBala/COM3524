from test_tool import get_results
import csv
from pathlib import Path

# Wind directions spread evenly around 360 degree circle
def run_wind_direction_possibilies(directions: int = 4, iterations_per_direction = 100):
    results = {}
    step = 360 / directions

    print(f"Running {directions} wind directions, spaced {step}° apart")
    print(f"Each direction will run for {iterations_per_direction} CA iterations.\n")

    for i in range(directions):
        direction = int(round(i * step))  # must be int for get_results
        print(f"--- Running direction: {direction}° ---")

        t = get_results(
            direction=direction,
            num_iterations=iterations_per_direction
        )

        print(f"→ Time for direction {direction}°: {t}\n")
        results[direction] = t

    print("All directions complete.\nSummary:")
    for d, t in results.items():
        print(f"  {d}° → time = {t}")

    return results

def save_results_to_csv(results, filename="wind_dir_effect_results.csv"):
    # Always save relative to THIS file’s directory
    csv_path = Path(__file__).parent / filename

    # Ensure the directory exists
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["direction", "time"])

        for direction, time_value in results.items():
            writer.writerow([direction, time_value])

    print(f"\nSaved results to: {csv_path.absolute()}\n")


if __name__ == "__main__":
    results = run_wind_direction_possibilies(4, 5)
    save_results_to_csv(results)
