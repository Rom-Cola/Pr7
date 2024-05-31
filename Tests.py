import unittest
import numpy as np
from main import update  # Замініть 'your_main_script' на ім'я вашого основного скрипта

class TestEpidemicModel(unittest.TestCase):

    def test_update_infected_to_recovered(self):
        grid_size = 10
        grid = np.zeros((grid_size, grid_size), dtype=int)
        time_infected = np.zeros((grid_size, grid_size), dtype=int)
        T_recover = 5
        P_infect = 0.2

        # Ініціалізація інфікованої клітини
        grid[5, 5] = 1
        time_infected[5, 5] = 4

        # Оновлення сітки
        new_grid, new_time_infected = update(grid, time_infected, P_infect, T_recover)

        # Перевірка, що інфікована клітина відновилась
        self.assertEqual(new_grid[5, 5], 2)
        self.assertEqual(new_time_infected[5, 5], 5)

    def test_update_susceptible_to_infected(self):
        grid_size = 10
        grid = np.zeros((grid_size, grid_size), dtype=int)
        time_infected = np.zeros((grid_size, grid_size), dtype=int)
        T_recover = 5
        P_infect = 1.0  # Встановлення високої ймовірності інфікування

        # Ініціалізація інфікованої клітини
        grid[5, 5] = 1

        # Оновлення сітки
        new_grid, new_time_infected = update(grid, time_infected, P_infect, T_recover)

        # Перевірка, що сусідня здорова клітина стала інфікованою
        self.assertEqual(new_grid[4, 5], 1)

    def test_no_infection_when_probability_is_zero(self):
        grid_size = 10
        grid = np.zeros((grid_size, grid_size), dtype=int)
        time_infected = np.zeros((grid_size, grid_size), dtype=int)
        T_recover = 5
        P_infect = 0.0  # Встановлення нульової ймовірності інфікування

        # Ініціалізація інфікованої клітини
        grid[5, 5] = 1

        # Оновлення сітки
        new_grid, new_time_infected = update(grid, time_infected, P_infect, T_recover)

        # Перевірка, що сусідня здорова клітина залишилась здоровою
        self.assertEqual(new_grid[4, 5], 0)

if __name__ == '__main__':
    unittest.main()
