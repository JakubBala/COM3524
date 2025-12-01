from concurrent.futures import ProcessPoolExecutor, as_completed
from test_tool import get_results
import csv
from pathlib import Path

def _run_single_direction(direction, iterations_per_direction):
    t = get_results(
        direction=direction,
        num_iterations=iterations_per_direction,
        start="INCINERATOR"
    )
    return direction, t

def run_wind_direction_possibilities(start_angle=-103, end_angle=77, iterations_per_direction=100):
    results = {}

    directions = list(range(start_angle, end_angle + 1))

    print(f"Running wind directions from {start_angle}° to {end_angle}°")
    print(f"Each direction will run for {iterations_per_direction} CA iterations.")
    print(f"Using {len(directions)} parallel tasks.\n")

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(_run_single_direction, d, iterations_per_direction): d
            for d in directions
        }

        for future in as_completed(futures):
            direction, t = future.result()
            print(f"→ Completed {direction}°: time = {t}")
            results[direction] = t

    print("\nAll directions complete.\nSummary:")
    for d in sorted(results.keys()):
        print(f"  {d}° → time = {results[d]}")

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
    results = run_wind_direction_possibilities(-52,128,1000)
    save_results_to_csv(results)
