
import math
import random

class Wind():
    def __init__(self, mean_speed: float, direction: int, weibull_k: float, weibull_c: float):
        self.mean_speed = mean_speed
        self.direction = direction
        self.weibull_k = weibull_k
        self.weibull_c = weibull_c

    def sample_wind_speed(self):
        u = random.random()
        return self.weibull_c * (-math.log(1 - u)) ** (1 / self.weibull_k)
    
    def _direction_difference(self, wind_dir, fire_dir):
        diff = abs(wind_dir - fire_dir) % 360
        if diff > 180:
            diff = 360 - diff

        return diff
    
    def fire_spread_contribution(self, fire_direction: int) -> float:
        w = self.sample_wind_speed()
        diff_deg = self._direction_difference(self.direction, fire_direction)
        theta = math.radians(diff_deg)

        f = min(w / 30.0, 1.0)

        # Gaussian
        sigma = 1.0 * (1 - f) + 0.3
        y = 0.1 + 0.9 * math.exp(-(theta / sigma)**2)

        # Scale
        y *= 0.5 + 0.5 * f

        return y

if __name__ == "__main__":
    speeds = [13.5, 13.9, 15.5, 15.5, 14.6, 14, 13.1, 12.5, 13.5, 13.5, 13.7, 13.4, 13.9]
    k, c = 37.284, 14.778

    print(f"Weibull K: {k:.3f}")
    print(f"Weibull C: {c:.3f}")

    mean_speed = sum(speeds)/len(speeds)
    print(f"Mean Speed: {mean_speed:.3f}")

    wind = Wind(mean_speed, direction=0, weibull_k=k, weibull_c=c)

    fire_dirs = [0, 45, 90, 135, 180, 225, 270, 315]

    for fd in fire_dirs:
        probs = [wind.fire_spread_contribution(fd) for _ in range(10)]
        avg_prob = sum(probs) / len(probs)
        print(f"  Fire direction {fd:3d}° → mean contribution: {avg_prob:.3f}")

    print("\nExample random wind speeds:")
    for _ in range(5):
        print(f"  {wind.sample_wind_speed():.2f} m/s")