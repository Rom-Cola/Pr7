import matplotlib
matplotlib.use('TkAgg')  # Використання TkAgg як бекенду для відображення графіків
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
from pymongo import MongoClient
import tkinter as tk
from tkinter import simpledialog
from concurrent.futures import ThreadPoolExecutor

# Визначення станів клітин
SUSCEPTIBLE = 0  # Здорова клітина
INFECTED = 1     # Інфікована клітина
RECOVERED = 2    # Відновлена клітина

# Ініціалізація параметрів за замовчуванням
default_grid_size = 50
default_P_infect = 0.2
default_T_recover = 5

# Підключення до MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['epidemic_model']
collection = db['simulation_steps']

def save_to_db(step, grid):
    data = {
        'step': step,
        'grid': grid.tolist()
    }
    collection.insert_one(data)

def update_cell(i, j, grid, time_infected, P_infect, T_recover):
    if grid[i, j] == INFECTED:
        time_infected[i, j] += 1
        if time_infected[i, j] >= T_recover:
            return RECOVERED, time_infected[i, j]
    elif grid[i, j] == SUSCEPTIBLE:
        neighbors = [
            grid[i-1, j] if i > 0 else SUSCEPTIBLE,
            grid[i+1, j] if i < grid.shape[0]-1 else SUSCEPTIBLE,
            grid[i, j-1] if j > 0 else SUSCEPTIBLE,
            grid[i, j+1] if j < grid.shape[1]-1 else SUSCEPTIBLE
        ]
        if INFECTED in neighbors and np.random.random() < P_infect:
            return INFECTED, 0
    return grid[i, j], time_infected[i, j]

def update(grid, time_infected, P_infect, T_recover):
    new_grid = grid.copy()
    new_time_infected = time_infected.copy()
    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                futures.append(executor.submit(update_cell, i, j, grid, time_infected, P_infect, T_recover))
        for future in futures:
            result = future.result()
            idx = futures.index(future)
            i = idx // grid.shape[1]
            j = idx % grid.shape[1]
            new_grid[i, j] = result[0]
            new_time_infected[i, j] = result[1]
    return new_grid, new_time_infected

# Визначення кольорової карти
cmap = ListedColormap(['green', 'red', 'purple'])

def start_simulation(grid_size, P_infect, T_recover):
    grid = np.zeros((grid_size, grid_size), dtype=int)
    time_infected = np.zeros((grid_size, grid_size), dtype=int)
    grid[grid_size//2, grid_size//2] = INFECTED

    fig, ax = plt.subplots()

    def animate(frame):
        nonlocal grid, time_infected
        grid, time_infected = update(grid, time_infected, P_infect, T_recover)
        save_to_db(frame, grid)  # Збереження стану в базу даних
        ax.clear()
        ax.imshow(grid, cmap=cmap, vmin=0, vmax=2)
        ax.set_title(f'Step: {frame}')

    ani = FuncAnimation(fig, animate, frames=200, interval=100)
    plt.show()

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()  # Сховати основне вікно

    grid_size = simpledialog.askinteger("Input", "Enter grid size:", initialvalue=default_grid_size)
    P_infect = simpledialog.askfloat("Input", "Enter infection probability (P_infect):", initialvalue=default_P_infect)
    T_recover = simpledialog.askinteger("Input", "Enter recovery time (T_recover):", initialvalue=default_T_recover)

    root.destroy()
    start_simulation(grid_size, P_infect, T_recover)
